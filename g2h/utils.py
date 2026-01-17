import subprocess
from pathlib import Path

def run_subprocess(cmd: list[str], cwd : Path, raise_on_error: bool = True):
    
    print(cmd)
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            # capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except KeyboardInterrupt:
        if raise_on_error:
            raise RuntimeError("Interrupted by user.") from None
        print("\n[Info] Interrupted.")
        return None

    if result.returncode != 0 and raise_on_error:
        raise RuntimeError(f"Command failed: {cmd}")

    return result
