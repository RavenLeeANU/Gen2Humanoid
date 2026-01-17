import argparse
import viser
import time

from .robot_viser import MJCFViserPlayer
from .smplx_viser import SMPLXViserPlayer

from pathlib import Path

def parse_args():
    ap = argparse.ArgumentParser("SMPL-X vs Robot Viser Player")

    ap.add_argument("--fps", type=float, default=None)

    # SMPL-X
    ap.add_argument("--smplx_path", type=Path, required=True)
    ap.add_argument("--smplx_motion", type=Path, required=True)
    ap.add_argument("--smplx_scale", type=float, default=1.0)
    ap.add_argument("--smplx_offset", type=float, nargs=3, default=[0,0,0])

    # Robot
    ap.add_argument("--robot_xml", type=Path, required=True)
    ap.add_argument("--robot_motion", type=Path, required=True)
    ap.add_argument("--robot_scale", type=float, default=1.0)
    ap.add_argument("--robot_offset", type=float, nargs=3, default=[0,0,0])

    return ap.parse_args()

def play(fps, smplx_path = None, smplx_motion  = None, robot_path  = None, robot_motion  = None):
    cmp = viser.ViserServer()
    cmp.scene.set_up_direction("+y")
    cmp.scene.add_grid("/grid", plane="xz")
    
    if smplx_path and smplx_motion:
        smplx_player = SMPLXViserPlayer(smplx_model_path=smplx_path, server=cmp)
        smplx_player.load_anim(smplx_motion)
        smplx_player.set_position([0,0,0])
    if robot_path and robot_motion:
        robot_player = MJCFViserPlayer(xml_path=robot_path, server=cmp)
        robot_player.load_anim(robot_motion)
        robot_player.set_position([1,0.7,0])

    if smplx_player:
        smplx_player.server = cmp
    
    if robot_player:
        robot_player.server = cmp

    dt = 1.0 / fps
    loop = True

    while True:
        t0 = time.time()

        if smplx_player:
            robot_player.get_frame(robot_player.cur_frame)
            robot_player.cur_frame += 1

            if robot_player.cur_frame >= robot_player.T:
                if loop:
                    robot_player.cur_frame = 0
                else:
                    break
        
        if smplx_player:
            smplx_player.get_frame(smplx_player.cur_frame)
            smplx_player.cur_frame += 1

            if smplx_player.cur_frame >= smplx_player.T:
                if loop:
                    smplx_player.cur_frame = 0
                else:
                    break

        sleep = dt - (time.time() - t0)
        if sleep > 0:
            time.sleep(sleep)

def main():
    args = parse_args()
    play(args.fps, args.smplx_path, args.robot_xml, args.smplx_motion, args.robot_motion)

if __name__ == "__main__":
    main()