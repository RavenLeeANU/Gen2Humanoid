#!/usr/bin/env python3

"""
Run the Gen2Humanoid pipeline

Step1. Generate motion 
Step2. Convert smpl format
Step3. Retarget to humanoid


"""

import argparse
import sys
import shutil
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from g2h.config import PROJECT_ROOT,HYM_DIR, GMR_DIR, HYM_CHECKPOINT_DIR, PROMPT_FOLDER
from g2h.utils import run_subprocess 
from g2h.convert_smpl import convert_to_smplx

def run_t2m(
    model_path : str,
    input_text_dir: Path,
    output_dir: Path,
    disable_duration_est : bool = False,
    disable_rewrite : bool = False
):  
    
    script_path = HYM_DIR / "local_infer.py"
    model_path = HYM_CHECKPOINT_DIR / model_path
    argv = [
        "python",
        str(script_path),
        "--model_path",
        str(model_path),
        "--input_text_dir",
        str(input_text_dir),
        "--output_dir",
        str(output_dir)
    ]

    run_subprocess(argv, HYM_DIR)

def run_convert(
    input_dir: Path,
    output_dir: Path
):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    input_path = Path(input_dir) / PROMPT_FOLDER
    npz_files = list(input_path.rglob("*.npz"))

    success_count = 0
    for input_file in npz_files:
        rel_path = input_file.relative_to(input_path)
        output_file = Path(output_dir) / rel_path

        output_file.parent.mkdir(parents=True, exist_ok=True)
        convert_to_smplx(input_file,output_file)
        success_count += 1

    print(f"\n处理完成！成功处理 {success_count}/{len(npz_files)} 个文件")
    print(f"输出目录: {output_dir}")

def run_retarget(
    robot_type : str, 
    input_dir : Path,
    output_dir : Path
):
   
    script_path = GMR_DIR / "scripts" / "smplx_to_robot_dataset.py"

    argv = [
        "python",
        str(script_path),
        "--src_folder",
        str(input_dir),
        "--robot",
        str(robot_type),
        "--tgt_folder",
        str(output_dir)
    ]

    print(argv)
    run_subprocess(argv, GMR_DIR)

def main():
    parser = argparse.ArgumentParser(
        description="Generate Motion to Robot Motion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    env_group = parser.add_argument_group("Text to Motion Setting")
    env_group.add_argument("--input_text_dir", default="data/t2m/example_subset.json", help="the directory of json files which records prompts.")
    env_group.add_argument("--output_dir", default="", help="text to motion output directory.")
    env_group.add_argument("--t2m_model", choices=["HY-Motion-1.0","HY-Motion-1.0-Lite"], help="currently supports HY-Motion-1.0 and HY-Motion-1.0-Lite.")

    env_group = parser.add_argument_group("Motion Retarget Setting")
    env_group.add_argument("--src_folder", default="", help="prompt")
    env_group.add_argument("--tgt_folder", default="", help="")
    env_group.add_argument("--robot_type", default="", help="")

    args = parser.parse_args()
    
    # step1
    run_t2m(model_path=args.t2m_model, input_text_dir=args.input_text_dir, output_dir=args.output_dir)

    # step2
    run_convert(input_dir=args.output_dir, output_dir=args.src_folder)

    # step3
    run_retarget(input_dir=args.src_folder, output_dir=args.tgt_folder, robot_type=args.robot_type)

if __name__ == "__main__":
    main()

    