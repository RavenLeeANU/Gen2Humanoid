from __future__ import annotations
import time
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import trimesh
import viser
import xml.etree.ElementTree as ET
from scipy.spatial.transform import Rotation as R

def quat_wxyz_to_xyzw(q):
    return np.array([q[1], q[2], q[3], q[0]], dtype=np.float32)

def parse_floats(s, n, default):
    if s is None:
        return np.asarray(default, dtype=np.float32)
    arr = np.fromstring(s, sep=" ", dtype=np.float32)
    assert arr.size == n
    return arr

T_ZUP_TO_YUP = np.array(
    [[1, 0, 0],
     [0, 1, 0],
     [0, 0, 1]],
    dtype=np.float32
)

def load_robot_visual_geoms(xml_path: Path):
    tree = ET.parse(str(xml_path))
    root = tree.getroot()

    compiler = root.find("compiler")
    meshdir = compiler.attrib.get("meshdir", "") if compiler is not None else ""
    mesh_base = (xml_path.parent / meshdir).resolve()

    asset_mesh = {}
    asset = root.find("asset")
    for m in asset.findall("mesh"):
        name = m.attrib["name"]
        file = m.attrib["file"]
        scale = parse_floats(m.attrib.get("scale"), 3, (1,1,1))
        asset_mesh[name] = (mesh_base / file, scale)

    body_geoms = {}

    def visit(body):
        name = body.attrib.get("name", "")
        geoms = []

        for g in body.findall("geom"):
            if g.attrib.get("type") != "mesh":
                continue

            mesh_name = g.attrib["mesh"]
            path, scale = asset_mesh[mesh_name]
            mesh = trimesh.load(path, force="mesh")
            mesh.vertices *= scale
            mesh.fix_normals()

            pos = parse_floats(g.attrib.get("pos"), 3, (0,0,0))
            quat = quat_wxyz_to_xyzw(
                parse_floats(g.attrib.get("quat"), 4, (1,0,0,0))
            )

            T = np.eye(4)
            T[:3,:3] = R.from_quat(quat).as_matrix()
            T[:3, 3] = pos
            mesh.apply_transform(T)

            rgba = parse_floats(g.attrib.get("rgba"), 4, (0.7,0.7,0.7,1))
            color = tuple((rgba[:3] * 255).astype(int))
            mesh.visual = trimesh.visual.ColorVisuals(mesh, face_colors=[*color,255])

            geoms.append(mesh)

        if geoms:
            body_geoms[name] = geoms

        for c in body.findall("body"):
            visit(c)

    worldbody = root.find("worldbody")
    visit(worldbody.find("body"))
    return body_geoms

class KinematicsModelLite:
    def __init__(self, xml_path):
        self.body_names = []
        self.parents = []
        self.local_pos = []
        self.local_quat = []
        self.joint_axes = []
        self.joint_dofs = []

        self._parse(xml_path)
        self.num_dof = sum(self.joint_dofs)

    def _parse(self, xml_path):
        tree = ET.parse(str(xml_path))
        root = tree.getroot()
        world = root.find("worldbody")
        body0 = world.find("body")

        def dfs(body, parent):
            idx = len(self.body_names)
            self.body_names.append(body.attrib.get("name", f"body_{idx}"))
            self.parents.append(parent)

            self.local_pos.append(parse_floats(body.attrib.get("pos"), 3, (0,0,0)))
            self.local_quat.append(
                quat_wxyz_to_xyzw(
                    parse_floats(body.attrib.get("quat"), 4, (1,0,0,0))
                )
            )

            joints = body.findall("joint")
            if len(joints) == 1:
                axis = parse_floats(joints[0].attrib.get("axis"), 3, (0,0,1))
                self.joint_axes.append(axis)
                self.joint_dofs.append(1)
            else:
                self.joint_axes.append(None)
                self.joint_dofs.append(0)

            for c in body.findall("body"):
                dfs(c, idx)

        dfs(body0, -1)

    def forward(self, root_pos, root_rot, dof):
        N = root_pos.shape[0]
        B = len(self.body_names)

        pos = np.zeros((N,B,3))
        rot = np.zeros((N,B,4))
        pos[:,0] = root_pos
        rot[:,0] = root_rot

        di = 0
        for i in range(1,B):
            p = self.parents[i]
            lp = self.local_pos[i]
            lq = self.local_quat[i]

            if self.joint_dofs[i] == 1:
                axis = self.joint_axes[i]
                ang = dof[:,di]
                di += 1
                dq = R.from_rotvec(axis * ang[:,None]).as_quat()
            else:
                dq = np.tile([0,0,0,1], (N,1))

            rot[:,i] = (
                R.from_quat(rot[:,p]) *
                R.from_quat(lq) *
                R.from_quat(dq)
            ).as_quat()

            pos[:,i] = pos[:,p] + R.from_quat(rot[:,p]).apply(lp)

        return pos, rot

class MJCFViserPlayer:
    def __init__(self, xml_path, server = None):
        self.xml_path = xml_path

        self.server = server
    
        self.root = self.server.scene.add_frame("/robot_root")

        self.frames = {}
        self.kin = KinematicsModelLite(xml_path)

        self.pos = None
        self.rot = None
        self.T = 0
        self.fps = 30
        self.cur_frame = 0

        self._load_visuals()

    def _load_visuals(self):
        geoms = load_robot_visual_geoms(self.xml_path)

        for name in geoms:
            f = self.server.scene.add_frame(f"/robot_root/{name}",show_axes=False)
            
            self.frames[name] = f
            for i, m in enumerate(geoms[name]):
                self.server.scene.add_mesh_trimesh(
                    f"/robot_root/{name}/geom_{i}", m
                )

    def load_anim(self, motion_pkl: Path):
        with open(motion_pkl, "rb") as f:
            motion = pickle.load(f)

        root_pos = motion["root_pos"]
        root_rot = motion["root_rot"]
        dof = motion["dof_pos"]
        self.fps = motion["fps"]

        pos, rot = self.kin.forward(root_pos, root_rot, dof)

        pos = pos @ T_ZUP_TO_YUP
        rot = R.from_quat(rot.reshape(-1,4)).as_matrix()
        rot = np.einsum("ij,njk->nik", T_ZUP_TO_YUP.T, rot)
        rot = R.from_matrix(rot).as_quat().reshape(pos.shape[0],-1,4)

        self.pos = pos
        self.rot = rot
        self.T = pos.shape[0]
        self.cur_frame = 0

    def get_frame(self, frame: Optional[int] = None):
        if frame is None:
            frame = self.cur_frame

        for i, name in enumerate(self.kin.body_names):
            if name in self.frames:
                self.frames[name].position = self.pos[frame, i]
                self.frames[name].wxyz = np.roll(self.rot[frame, i], 1)

    def get_frame_count(self):
        return self.T

    def get_cur_frame(self):
        return self.cur_frame

    def reset_cur_frame(self):
        self.cur_frame = 0

    def set_scale(self, scale: float):
        self.root.scale = scale

    def set_position(self, position):
        self.root.position = np.array(position)

    def play(self, loop=True):
        dt = 1.0 / self.fps
        while True:
            self.get_frame(self.cur_frame)
            self.cur_frame += 1
            if self.cur_frame >= self.T:
                if loop:
                    self.cur_frame = 0
                else:
                    break
            time.sleep(dt)

if __name__ == "__main__":
    
    server = viser.ViserServer()

    player = MJCFViserPlayer(
        server=server,
        xml_path=Path("/home/liwenrui/liwenrui/OpenSource/Gen2Humanoid/third_party/GMR/assets/unitree_g1/g1_mocap_29dof.xml")
    )

    player.load_anim(Path("outputs/gmr/B18_-_walk_to_leap_to_walk_stageii.pkl"))
    player.set_position(np.array([0,0,0]))

    player.play()