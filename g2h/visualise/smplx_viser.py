from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import viser
import smplx


class SMPLXViserPlayer:
    def __init__(
        self,
        smplx_model_path: Path,
        server = None,
        device: torch.device = torch.device("cpu")
    ):
        self.device = device

        self.model = smplx.create(
            model_path=str(smplx_model_path.parent),
            model_type="smplx",
            gender="neutral",
            use_pca=False,
            batch_size=1,
        ).to(device)

        self.server = server
    
        # root frame (for scale / position)
        self.root = self.server.scene.add_frame("/human_root")
        self.root.scale = 10.0

        # mesh handle
        self.mesh = None

        self.cur_frame = 0
        self.T = 0
        self.fps = 30

        # motion buffers
        self.betas = None
        self.root_orient = None
        self.pose_body = None
        self.pose_hand = None
        self.pose_jaw = None
        self.pose_eye = None
        self.trans = None

    def load_anim(self, motion_npz: Path):
        """Load AMASS / SMPL-X motion"""
        data = np.load(motion_npz, allow_pickle=True)

        self.fps = int(data["mocap_frame_rate"])
        self.T = data["root_orient"].shape[0]
        self.cur_frame = 0

        self.betas = torch.tensor(
            data["betas"],
            device=self.device,
        ).float()

        self.root_orient = torch.tensor(data["root_orient"], device=self.device).float()
        self.pose_body = torch.tensor(data["pose_body"], device=self.device).float()
        self.pose_hand = torch.tensor(data["pose_hand"], device=self.device).float()
        self.pose_jaw = torch.tensor(data["pose_jaw"], device=self.device).float()
        self.pose_eye = torch.tensor(data["pose_eye"], device=self.device).float()
        self.trans = torch.tensor(data["trans"], device=self.device).float()

        gender = str(data["gender"])
        self.model.gender = gender

        # ===== init mesh =====
        with torch.no_grad():
            out = self.model(
                betas=self.betas.unsqueeze(0),
                body_pose=torch.zeros(1, 63, device=self.device),
                global_orient=torch.zeros(1, 3, device=self.device),
                transl=torch.zeros(1, 3, device=self.device),
            )

        if self.mesh is None:
            self.mesh = self.server.scene.add_mesh_simple(
                "/human_root/human",
                out.vertices[0].cpu().numpy(),
                self.model.faces,
                color=(180, 200, 255),
            )
        else:
            self.mesh.vertices = out.vertices[0].cpu().numpy()

    def get_frame(self, frame: Optional[int] = None):
        """Update mesh to a specific frame (or current frame)"""
        if frame is None:
            frame = self.cur_frame

        with torch.no_grad():
            out = self.model(
                betas=self.betas.unsqueeze(0),
                global_orient=self.root_orient[frame].unsqueeze(0),
                body_pose=self.pose_body[frame].unsqueeze(0),
                left_hand_pose=self.pose_hand[frame, :45].unsqueeze(0),
                right_hand_pose=self.pose_hand[frame, 45:].unsqueeze(0),
                jaw_pose=self.pose_jaw[frame].unsqueeze(0),
                leye_pose=self.pose_eye[frame, :3].unsqueeze(0),
                reye_pose=self.pose_eye[frame, 3:].unsqueeze(0),
                transl=self.trans[frame].unsqueeze(0),
            )

        self.mesh.vertices = out.vertices[0].cpu().numpy()

    def get_frame_count(self) -> int:
        return self.T

    def get_cur_frame(self) -> int:
        return self.cur_frame

    def reset_cur_frame(self):
        self.cur_frame = 0

    def set_scale(self, scale: float):
        """Scale the whole human"""
        self.root.dimensions = scale

    def set_position(self, position):
        """Move the whole human (xyz)"""
        self.root.position = np.array(position)


if __name__ == "__main__":

    server = viser.ViserServer()
    player = SMPLXViserPlayer(
    server,
    smplx_model_path=Path("/home/liwenrui/liwenrui/Projects/GMR/assets/body_models/smplx/"),
    device=torch.device("cpu"),
    )

    player.load_anim(
        Path("/home/liwenrui/liwenrui/Data/AMASS-SMPLXN/AMASS/ACCAD/Female1Gestures_c3d/D1_-_Urban_1_stageii.npz")
    )

    player.set_position(np.array([0.0, 0.0, 0.0]))

    fps = 30
    dt = 1.0 / fps
    loop = True
    while True:
        t0 = time.time()

        player.get_frame(player.cur_frame)
        player.cur_frame += 1

        if player.cur_frame >= player.T:
            if loop:
                player.cur_frame = 0
            else:
                break

        sleep = dt - (time.time() - t0)
        if sleep > 0:
            time.sleep(sleep)