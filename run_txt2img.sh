#!/bin/bash

cd /home/mika/prj/stablediffusion/
python scripts/txt2img.py --prompt "$1" --seed $RANDOM --ckpt ~/Downloads/v2-1_768-ema-pruned.ckpt --config configs/stable-diffusion/v2-inference-v.yaml --H 768 --W 768
