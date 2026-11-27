"""
TV2 - Hàm suy luận bàn giao cho TV4 (Superset) và TV5 (web app).

    from predict import classify_article
    kq = classify_article("Giả danh công an, ép nữ sinh thuê nhà nghỉ để lừa 300 triệu đồng ...")

Mặc định dùng TF-IDF + Logistic Regression (models/nlp_tfidf_lr.pkl) vì cho Macro-F1 cao nhất
khi đánh giá 5-fold và chạy nhẹ. Có thể dùng PhoBERT đã fine-tune bằng cách đặt biến môi trường
NLP_MODEL=phobert (cần torch, transformers và thư mục models/phobert_scam_cls).

Chạy hàng loạt cho bảng news_articles (để TV1/TV4 nạp vào CSDL):
    python nlp/predict.py --csv data/processed/news_articles.csv --out data/nlp/news_articles_predicted.csv
"""
import argparse
import os
import sys

import joblib
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manual_labels import GROUPS  # noqa: E402
from text_utils import clean_text, extract_entities, tokenize  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOBERT_DIR = os.path.join(BASE, "models", "phobert_scam_cls")
TFIDF_PATH = os.path.join(BASE, "models", "nlp_tfidf_lr.pkl")
NAME2DESC = {v[0]: (v[1], v[2]) for v in GROUPS.values()}
_cache = {}


def _load():
    if "kind" in _cache:
        return _cache
    if os.environ.get("NLP_MODEL", "tfidf") != "phobert":
        _cache.update(kind="tfidf", bundle=joblib.load(TFIDF_PATH))
        return _cache
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        if not os.path.isdir(PHOBERT_DIR):
            raise FileNotFoundError(PHOBERT_DIR)
        _cache.update(kind="phobert", torch=torch,
                      tok=AutoTokenizer.from_pretrained(PHOBERT_DIR),
                      model=AutoModelForSequenceClassification.from_pretrained(PHOBERT_DIR).float().eval())  # trọng số lưu fp16 cho nhẹ
    except Exception as e:  # không có torch hoặc chưa có trọng số
        print("[predict] Dùng TF-IDF + LR vì:", e, file=sys.stderr)
        _cache.update(kind="tfidf", bundle=joblib.load(TFIDF_PATH))
    return _cache


def _proba(texts):
    c = _load()
    if c["kind"] == "phobert":
        from pyvi import ViTokenizer
        segs = [ViTokenizer.tokenize(clean_text(t)) for t in texts]
        enc = c["tok"](segs, truncation=True, max_length=96, padding=True, return_tensors="pt")
        with c["torch"].no_grad():
            p = c["torch"].softmax(c["model"](**enc).logits, -1).numpy()
        labels = [c["model"].config.id2label[i] for i in range(p.shape[1])]
    else:
        m = c["bundle"]["model"]
        p = m.predict_proba([tokenize(t) for t in texts])
        labels = list(m.classes_)
    return p, labels


def classify_article(text: str, top_k: int = 3) -> dict:
    p, labels = _proba([text])
    p = p[0]
    order = np.argsort(-p)[:top_k]
    best = labels[order[0]]
    ents = extract_entities(text)
    return {
        "nhom_thu_doan": best,
        "mo_ta": NAME2DESC[best][0],
        "ma_scam_lien_quan": NAME2DESC[best][1],
        "do_tin_cay": round(float(p[order[0]]), 4),
        "top_k": [(labels[i], round(float(p[i]), 4)) for i in order],
        "la_bai_lua_dao": best != "KHONG_PHAI_LUA_DAO",
        **ents,
        "mo_hinh": "PhoBERT fine-tune" if _cache["kind"] == "phobert" else "TF-IDF + Logistic Regression",
    }


def classify_csv(path_in, path_out, text_col="clean_content"):
    import pandas as pd
    df = pd.read_csv(path_in)
    rows = [classify_article(t) for t in df[text_col].fillna("")]
    for k in ("nhom_thu_doan", "do_tin_cay", "ma_scam_lien_quan"):
        df["pred_" + k] = [r[k] for r in rows]
    for k in ("to_chuc_bi_gia_mao", "kenh_lien_lac"):
        df["pred_" + k] = ["; ".join(r[k]) for r in rows]
    df.to_csv(path_out, index=False, encoding="utf-8-sig")
    print("Đã ghi", path_out, len(df), "bài")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv")
    ap.add_argument("--out", default=os.path.join(BASE, "data", "nlp", "news_articles_predicted.csv"))
    ap.add_argument("text", nargs="*")
    a = ap.parse_args()
    if a.csv:
        classify_csv(a.csv, a.out)
    else:
        import json
        for t in a.text or ["Giả danh công an, ép nữ sinh thuê nhà nghỉ để tự cô lập rồi yêu cầu chuyển 300 triệu đồng"]:
            print(json.dumps(classify_article(t), ensure_ascii=False, indent=2))
