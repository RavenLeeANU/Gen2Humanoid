
import argparse
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from g2h.visualise import play
from g2h.config import GMR_BODY_MODELS_DIR, ROBOT_XML_DICT


def main():
    parser = argparse.ArgumentParser(
        description="Generate Motion to Robot Motion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    env_group = parser.add_argument_group("Text to Motion Setting")
    env_group.add_argument("--fps", default=30, help="fps")
    env_group.add_argument("--robot", default=None, help="robot type")
    env_group.add_argument("--show_smplx", default=None, help="show smplx")
    env_group.add_argument("--robot_motion", default=None, help="robot motion path")
    env_group.add_argument("--smplx_motion", default=None, help="smplx motion path")

    args = parser.parse_args()

    use_robot = args.robot is not None
    use_smplx = args.show_smplx is not None

    if not use_robot and not use_smplx:
        parser.error(
            "At least one of --robot or --show_smplx must be specified."
        )

    if use_robot and args.robot_motion is None:
        parser.error(
            "--robot is specified but --robot_motion is missing."
        )

    if use_smplx and args.smplx_motion is None:
        parser.error(
            "--show_smplx is specified but --smplx_motion is missing."
        )

    robot_path = None
    if args.robot:
        robot_path = ROBOT_XML_DICT[args.robot]
    
    play(args.fps, smplx_path=GMR_BODY_MODELS_DIR, smplx_motion=args.smplx_motion, robot_path=robot_path, robot_motion=args.robot_motion)



if __name__ == "__main__":
    main()
