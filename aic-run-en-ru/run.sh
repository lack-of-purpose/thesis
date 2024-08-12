#!/bin/bash
#SBATCH -J xlm-r-ft
#SBATCH -p gpu -G 1
#SBATCH --mem=64G
#SBATCH -o stdout.txt
#SBATCH -e error.txt

pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip3 install -U optuna transformers datasets pandas scikit-learn hyperopt xgboost SentencePiece wandb unbabel-comet lightning torchmetrics
pip3 install accelerate -U
export WANDB_API_KEY=52417aeb280e54ec9b4c205a8979c18f4456a44e
wandb login
python3 xlm-r-ft-optuna.py
