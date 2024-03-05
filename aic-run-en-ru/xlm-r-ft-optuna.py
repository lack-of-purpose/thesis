import pandas as pd
import csv
import torch
import datasets
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.metrics import matthews_corrcoef, roc_auc_score
import optuna
import os

#os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["WANDB_MODE"] = "disabled"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:2048"

def preprocess_function(examples):
    return tokenizer(examples["source"], examples["target"], padding=False, truncation=True)

def model_init(trial):
    return AutoModelForSequenceClassification.from_pretrained(
        model_checkpoint,
        from_tf=bool(".ckpt" in model_checkpoint)
    )

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    matt = matthews_corrcoef(labels, preds)
    roc_auc = roc_auc_score(labels, preds)
    return {"roc_auc": roc_auc, "mcc": matt}

def objective(trial):
    torch.cuda.empty_cache()
    per_device_train_batch_size = trial.suggest_categorical("per_device_train_batch_size", [16, 32])
    args = TrainingArguments(
        f"{model_name}-finetuned",
        evaluation_strategy="steps",
        save_strategy="no",
        eval_steps=100,
        num_train_epochs=5,
        load_best_model_at_end=False,
        push_to_hub=False,
        seed=42,
        lr_scheduler_type='constant_with_warmup',
        learning_rate=trial.suggest_loguniform("learning_rate", 1e-6, 1e-4),
        weight_decay=trial.suggest_loguniform("weight_decay", 1e-6, 5e-4),
        warmup_steps=trial.suggest_categorical("warmup_steps", [500, 700, 1000]),
        per_device_train_batch_size=per_device_train_batch_size
    )
    
    args.per_device_eval_batch_size = per_device_train_batch_size

    trainer = Trainer(
        args=args,
        train_dataset=encoded_dataset["train"],
        eval_dataset=encoded_dataset["val"],
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        model_init=model_init
    )

    trainer.train()
    metrics = trainer.evaluate()
    return metrics["eval_loss"]

if __name__ == "__main__":
    model_checkpoint = "xlm-roberta-base"
    df_train = pd.read_csv('training-ru-95-src-tgt.csv', sep='|', quoting=csv.QUOTE_NONE, encoding='utf-8')
    df_test = pd.read_csv('test-ru-95-src-tgt.csv', sep='|', encoding='utf-8')
    df_val = pd.read_csv('validation-ru-95-src-tgt.csv', sep='|', encoding='utf-8')

    df_train['labels'] = df_train['labels'].map({'mt': 0, 'human': 1})
    df_test['labels'] = df_test['labels'].map({'mt': 0, 'human': 1})
    df_val['labels'] = df_val['labels'].map({'mt': 0, 'human': 1})

    dataset = datasets.DatasetDict({
        "train": datasets.Dataset.from_pandas(df_train),
        "test": datasets.Dataset.from_pandas(df_test),
        "val": datasets.Dataset.from_pandas(df_val),
    })

    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint, use_fast=True)
    encoded_dataset = dataset.map(preprocess_function, batched=True, batch_size=None)

    num_labels = 2
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = (AutoModelForSequenceClassification.from_pretrained(model_checkpoint, num_labels=num_labels).to(device))

    model_name = model_checkpoint.split("/")[-1]

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=30)

    print("Study statistics:")
    print("  Number of finished trials:", len(study.trials))
    print("  Best trial:")
    best_trial = study.best_trial
    print("    Value: {}".format(best_trial.value))
    print("    Params: ")
    for key, value in best_trial.params.items():
        print("      {}: {}".format(key, value))

    print("\nAll trials:")
    for trial in study.trials:
        print("  Trial number:", trial.number)
        print("    Value: {}".format(trial.value))
        print("    Params: ")
        for key, value in trial.params.items():
            print("      {}: {}".format(key, value))
