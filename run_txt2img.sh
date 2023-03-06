#!/bin/bash

cd /home/mika/prj/stablediffusion/

if [[ ! -z "$2" ]]; then
  python scripts/img2img.py --prompt "$1" --init-img "$2" --strength 0.5 --n_samples 4 --seed $RANDOM --ckpt ~/Downloads/v2-1_768-ema-pruned.ckpt --config configs/stable-diffusion/v2-inference-v.yaml
else
  python scripts/txt2img.py --prompt "$1" --seed $RANDOM --ckpt ~/Downloads/v2-1_768-ema-pruned.ckpt --config configs/stable-diffusion/v2-inference-v.yaml --H 768 --W 768
fi
