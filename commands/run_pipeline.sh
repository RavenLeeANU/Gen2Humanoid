#!/usr/bin/env bash

python scripts/pipeline.py \
    --input_text_dir /home/liwenrui/liwenrui/OpenSource/Gen2Humanoid/data/t2m/example_subset.json \
    --output_dir /home/liwenrui/liwenrui/OpenSource/Gen2Humanoid/outputs/t2m \
    --t2m_model HY-Motion-1.0 \
    --robot_type unitree_g1 \
    --src_folder /home/liwenrui/liwenrui/OpenSource/Gen2Humanoid/outputs/cvt \
    --tgt_folder /home/liwenrui/liwenrui/OpenSource/Gen2Humanoid/outputs/gmr
