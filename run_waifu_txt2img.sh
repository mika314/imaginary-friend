#!/bin/bash

cd /home/mika/prj/stablediffusion/
python scripts/txt2img.py --prompt "$1" --seed $RANDOM --ckpt ~/Downloads/wd-1-4-anime_e2.ckpt --config ~/Downloads/wd-1-4-anime_e1.yaml --H 768 --W 768
