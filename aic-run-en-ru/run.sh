#!/bin/bash
#SBATCH -J xlm-r-ft
#SBATCH -p gpu -G 1
#SBATCH --mem=128G
#SBATCH -o stdout.txt
#SBATCH -e error.txt


pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip3 install -U optuna transformers datasets pandas scikit-learn
pip3 install accelerate -U
python3 xlm-r-ft-optuna.py
