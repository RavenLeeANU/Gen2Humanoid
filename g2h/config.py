from __future__ import annotations

import os
import os
from pathlib import Path
from typing import Optional

from dataclasses import dataclass, field


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
THIRD_PARTY_DIR = PROJECT_ROOT / "third_party"
DATA_DIR = PROJECT_ROOT / "data"
CONFIGS_DIR = PROJECT_ROOT / "configs"
PROMPT_FOLDER = "prompts_subset"

# Third-party paths
HYM_DIR = THIRD_PARTY_DIR / "HY-Motion-1.0"
GMR_DIR = THIRD_PARTY_DIR / "GMR"

# Model paths (HYM)
HYM_CHECKPOINT_DIR = HYM_DIR / "ckpts" / "tencent"

# Model paths (GMR)
GMR_BODY_MODELS_DIR = GMR_DIR / "assets" / "body_models" / "smplx"

# Put your own robot config here
ROBOT_XML_DICT = {
    "unitree_g1": GMR_DIR / "assets" / "unitree_g1" / "g1_mocap_29dof.xml",
    "unitree_g1_with_hands": GMR_DIR / "assets" / "unitree_g1" / "g1_mocap_29dof_with_hands.xml",
    "unitree_h1": GMR_DIR / "assets" / "unitree_h1" / "h1.xml",
    "unitree_h1_2": GMR_DIR / "assets" / "unitree_h1_2" / "h1_2_handless.xml",
    "booster_t1": GMR_DIR / "assets" / "booster_t1" / "T1_serial.xml",
    "booster_t1_29dof": GMR_DIR / "assets" / "booster_t1_29dof" / "t1_mocap.xml",
    "stanford_toddy": GMR_DIR / "assets" / "stanford_toddy" / "toddy_mocap.xml",
    "fourier_n1": GMR_DIR / "assets" / "fourier_n1" / "n1_mocap.xml",
    "engineai_pm01": GMR_DIR / "assets" / "engineai_pm01" / "pm_v2.xml",
    "kuavo_s45": GMR_DIR / "assets" / "kuavo_s45" / "biped_s45_collision.xml",
    "hightorque_hi": GMR_DIR / "assets" / "hightorque_hi" / "hi_25dof.xml",
    "galaxea_r1pro": GMR_DIR / "assets" / "galaxea_r1pro" / "r1_pro.xml",
    "berkeley_humanoid_lite": GMR_DIR / "assets" / "berkeley_humanoid_lite" / "bhl_scene.xml",
    "booster_k1": GMR_DIR / "assets" / "booster_k1" / "K1_serial.xml",
    "pnd_adam_lite": GMR_DIR / "assets" / "pnd_adam_lite" / "scene.xml",
    "tienkung": GMR_DIR / "assets" / "tienkung" / "mjcf" / "tienkung.xml",
    "pal_talos": GMR_DIR / "assets" / "pal_talos" / "talos.xml",
    "fourier_gr3": GMR_DIR / "assets" / "fourier_gr3v2_1_1" / "mjcf" / "gr3v2_1_1_dummy_hand.xml",
}