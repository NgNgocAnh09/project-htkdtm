"""
TV2 - Bước 3: Fine-tune PhoBERT (vinai/phobert-base) phân loại nhóm thủ đoạn.

- Đầu vào: văn bản đã tách từ bằng PyVi (PhoBERT yêu cầu tách từ, VD 'lừa_đảo')
- Đánh giá: dùng lại đúng 5 fold (StratifiedGroupKFold theo sự kiện) của baseline -> so sánh công bằng
- Sau khi đánh giá, huấn luyện lại trên toàn bộ 247 bài và lưu trọng số vào models/phobert_scam_cls/
Chạy (CPU được, khoảng 25-35 phút): python nlp/train_phobert.py [--folds 0,1,2,3,4] [--final]
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd
import torch
from pyvi import ViTokenizer
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader, TensorDataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "nlp")
REP = os.path.join(BASE, "reports", "nlp")
MODEL_OUT = os.path.join(BASE, "models", "phobert_scam_cls")
NAME = "vinai/phobert-base"
MAXLEN, BS, EPOCHS, LR = 96, 8, 6, 3e-5
SEED = 42
torch.set_num_threads(os.cpu_count() or 2)


def seg(t):
    return ViTokenizer.tokenize(t)


def encode(tok, texts, labels=None):
    enc = tok(list(texts), truncation=True, max_length=MAXLEN, padding="max_length", return_tensors="pt")
    tensors = [enc["input_ids"], enc["attention_mask"]]
    if labels is not None:
        tensors.append(torch.tensor(labels))
    return TensorDataset(*tensors)


def train_one(tok, tr_texts, tr_y, n_labels, class_w):
    torch.manual_seed(SEED)
    model = AutoModelForSequenceClassification.from_pretrained(NAME, num_labels=n_labels)
    dl = DataLoader(encode(tok, tr_texts, tr_y), batch_size=BS, shuffle=True)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    steps = len(dl) * EPOCHS
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    loss_fn = torch.nn.CrossEntropyLoss(weight=torch.tensor(class_w, dtype=torch.float))
    model.train()
    for ep in range(EPOCHS):
        tot = 0
        for ids, mask, y in dl:
            out = model(input_ids=ids, attention_mask=mask)
            loss = loss_fn(out.logits, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sch.step(); opt.zero_grad()
            tot += loss.item()
        print(f"    epoch {ep + 1}/{EPOCHS} loss={tot / len(dl):.4f}", flush=True)
    return model


@torch.no_grad()
def predict_proba(model, tok, texts):
    model.eval()
    dl = DataLoader(encode(tok, texts), batch_size=16)
    out = [torch.softmax(model(input_ids=i, attention_mask=m).logits, -1).numpy() for i, m in dl]
    return np.vstack(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folds", default="0,1,2,3,4")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    os.makedirs(REP, exist_ok=True)

    df = pd.read_csv(os.path.join(DATA, "articles_labeled.csv"))
    folds = pd.read_csv(os.path.join(DATA, "cv_folds.csv"))
    df = df.merge(folds[["article_id", "fold"]], on="article_id")
    labels = sorted(df["label"].unique())
    l2i = {l: i for i, l in enumerate(labels)}
    y = df["label"].map(l2i).values
    texts = df["text"].map(seg).values
    cnt = np.bincount(y, minlength=len(labels))
    class_w = (len(y) / (len(labels) * cnt)) ** 0.5   # trọng số lớp (căn bậc hai để không quá gắt)
    tok = AutoTokenizer.from_pretrained(NAME)

    pred_path = os.path.join(REP, "du_doan_cv_phobert.csv")
    pred = pd.read_csv(pred_path) if os.path.exists(pred_path) else pd.DataFrame(
        {"article_id": df.article_id, "label": df.label, "phobert": None})
    for k in [int(x) for x in a.folds.split(",") if x != ""]:
        t0 = time.time()
        tr, te = (df.fold != k).values, (df.fold == k).values
        print(f"Fold {k}: train={tr.sum()} test={te.sum()}", flush=True)
        m = train_one(tok, texts[tr], y[tr], len(labels), class_w)
        p = predict_proba(m, tok, texts[te]).argmax(1)
        pred.loc[te, "phobert"] = [labels[i] for i in p]
        pred.to_csv(pred_path, index=False, encoding="utf-8-sig")
        print(f"  macro-F1 fold {k} = {f1_score(y[te], p, average='macro'):.4f}  ({time.time() - t0:.0f}s)", flush=True)
        del m

    if pred["phobert"].notna().all():
        f1 = f1_score(pred["label"], pred["phobert"], average="macro")
        print("PhoBERT macro-F1 (gộp 5 fold):", round(f1, 4))

    if a.final:
        print("Huấn luyện mô hình cuối trên toàn bộ dữ liệu...", flush=True)
        m = train_one(tok, texts, y, len(labels), class_w)
        m.config.id2label = {i: l for l, i in l2i.items()}
        m.config.label2id = l2i
        os.makedirs(MODEL_OUT, exist_ok=True)
        m.save_pretrained(MODEL_OUT, safe_serialization=True)
        tok.save_pretrained(MODEL_OUT)
        json.dump({"maxlen": MAXLEN, "epochs": EPOCHS, "lr": LR, "batch_size": BS, "base": NAME},
                  open(os.path.join(MODEL_OUT, "train_config.json"), "w"))
        print("Đã lưu", MODEL_OUT)


if __name__ == "__main__":
    main()
