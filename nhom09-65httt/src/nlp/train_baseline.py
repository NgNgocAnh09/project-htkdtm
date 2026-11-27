"""
TV2 - Bước 1+2: Tạo bộ dữ liệu gán nhãn, gom nhóm bài trùng sự kiện, chạy baseline.

Baseline:
  (1) Luật từ khóa
  (2) TF-IDF (từ đã tách bằng PyVi, 1-2 gram) + Logistic Regression
  (3) TF-IDF + Linear SVM

Đánh giá: 5-fold StratifiedGroupKFold. Các bài cùng một sự kiện (VD: VnExpress và Dân trí
cùng đưa tin vụ Sen Tài Thu) được xếp chung một nhóm để không vừa nằm ở train vừa ở test.
Chạy (đứng ở src/): python nlp/train_baseline.py
"""
import json
import os
import warnings

import joblib
import numpy as np
import pandas as pd
from scipy.sparse.csgraph import connected_components
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

from manual_labels import GROUPS, LABELS_BY_ROW
from text_utils import clean_text, extract_entities, tokenize

warnings.filterwarnings("ignore")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data", "nlp")
REP = os.path.join(BASE, "reports", "nlp")
MODEL_DIR = os.path.join(BASE, "models")
SEED = 42

KEYWORDS = {
    "A": ["giả danh công an", "giả danh cán bộ", "mạo danh", "bắt cóc online", "rửa tiền", "tài khoản an toàn", "thiếu tướng"],
    "B": ["đầu tư", "nhà đầu tư", "sàn", "huy động", "tiền ảo", "tiền số", "đa cấp", "forex", "crypto", "lợi nhuận"],
    "C": ["nhà ở xã hội", "đất", "sổ đỏ", "căn hộ", "suất ngoại giao", "bất động sản"],
    "D": ["đáo hạn", "vay", "hụi", "sổ tiết kiệm", "nhân viên ngân hàng", "cho vay"],
    "E": ["facebook", "tiktok", "telegram", "livestream", "fanpage", "mạng xã hội", "việc nhẹ lương cao", "tình cảm", "threads"],
    "F": ["bác sĩ", "thẩm mỹ", "phòng khám", "thực phẩm chức năng"],
    "G": ["chạy án", "chạy việc", "chạy biên chế", "chạy dự án", "chạy thủ tục", "quen biết lãnh đạo"],
    "H": ["tài khoản ngân hàng", "dữ liệu cá nhân", "mã độc", "mua bán tài khoản"],
    "K": ["chiếm đoạt", "lừa đảo"],
}


def keyword_predict(texts):
    out = []
    for t in texts:
        low = clean_text(t).lower()
        score = {k: sum(low.count(w) for w in ws) for k, ws in KEYWORDS.items()}
        best = max(score, key=score.get)
        out.append(best if score[best] > 0 else "I")
    return np.array(out)


def event_groups(texts, thr=0.45):
    """Gom các bài có độ tương đồng cosine TF-IDF >= thr thành một nhóm sự kiện."""
    X = TfidfVectorizer(ngram_range=(1, 2), min_df=1).fit_transform(texts)
    S = cosine_similarity(X) >= thr
    _, lab = connected_components(S, directed=False)
    return lab


def build_dataset():
    src = pd.read_csv(os.path.join(BASE, "data", "processed", "sample_articles_for_nlp_tv2.csv"))
    assert len(src) == len(LABELS_BY_ROW)
    df = src[["article_id", "title", "clean_content", "publisher", "publish_date_ict"]].copy()
    df["text"] = df["clean_content"].map(clean_text)
    df["label_code"] = [LABELS_BY_ROW[i] for i in range(len(df))]
    df["label"] = df["label_code"].map(lambda c: GROUPS[c][0])
    df["text_tok"] = df["text"].map(tokenize)
    df["event_group"] = event_groups(df["text_tok"])
    ents = df["text"].map(extract_entities)
    df["to_chuc_bi_gia_mao"] = ents.map(lambda e: "; ".join(e["to_chuc_bi_gia_mao"]))
    df["to_chuc_nhac_den"] = ents.map(lambda e: "; ".join(e["to_chuc_nhac_den"]))
    df["kenh_lien_lac"] = ents.map(lambda e: "; ".join(e["kenh_lien_lac"]))
    return df


def tfidf_lr():
    return make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                         LogisticRegression(max_iter=3000, C=10, class_weight="balanced"))


def tfidf_svm():
    return make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                         LinearSVC(C=1.0, class_weight="balanced"))


def main():
    os.makedirs(OUT, exist_ok=True); os.makedirs(REP, exist_ok=True); os.makedirs(MODEL_DIR, exist_ok=True)
    df = build_dataset()
    df.drop(columns=["clean_content"]).to_csv(os.path.join(OUT, "articles_labeled.csv"), index=False, encoding="utf-8-sig")
    print(df["label"].value_counts())
    print("Số nhóm sự kiện:", df["event_group"].nunique(), "/", len(df))

    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    folds = np.zeros(len(df), dtype=int)
    for k, (_, te) in enumerate(cv.split(df, df["label"], df["event_group"])):
        folds[te] = k
    df["fold"] = folds
    df[["article_id", "fold", "event_group"]].to_csv(os.path.join(OUT, "cv_folds.csv"), index=False)

    preds = {"Từ khóa (rule)": keyword_predict(df["text"])}
    preds["Từ khóa (rule)"] = np.array([GROUPS[c][0] for c in preds["Từ khóa (rule)"]])
    for name, mk in (("TF-IDF + Logistic Regression", tfidf_lr), ("TF-IDF + Linear SVM", tfidf_svm)):
        p = np.empty(len(df), dtype=object)
        for k in range(5):
            tr, te = df.fold != k, df.fold == k
            m = mk().fit(df.loc[tr, "text_tok"], df.loc[tr, "label"])
            p[te.values] = m.predict(df.loc[te, "text_tok"])
        preds[name] = p

    rows = []
    for name, p in preds.items():
        per_fold = [f1_score(df.label[df.fold == k], p[df.fold == k], average="macro") for k in range(5)]
        rows.append({"Mô hình": name,
                     "Macro-F1": round(f1_score(df.label, p, average="macro"), 4),
                     "Macro-F1 TB fold": round(np.mean(per_fold), 4), "Độ lệch chuẩn": round(np.std(per_fold), 4),
                     "Weighted-F1": round(f1_score(df.label, p, average="weighted"), 4),
                     "Accuracy": round(np.mean(p == df.label.values), 4)})
        print(f"\n=== {name} ===\n", classification_report(df.label, p, zero_division=0))
    res = pd.DataFrame(rows)
    print(res.to_string(index=False))
    res.to_csv(os.path.join(REP, "ket_qua_baseline.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame({k: v for k, v in preds.items()} | {"article_id": df.article_id, "label": df.label}).to_csv(
        os.path.join(REP, "du_doan_cv_baseline.csv"), index=False, encoding="utf-8-sig")

    # Lưu mô hình TF-IDF + LR huấn luyện trên toàn bộ dữ liệu (dùng làm mô hình dự phòng nhẹ)
    final = tfidf_lr().fit(df["text_tok"], df["label"])
    joblib.dump({"model": final, "labels": {v[0]: v[1] for v in GROUPS.values()}, "version": "1.0"},
                os.path.join(MODEL_DIR, "nlp_tfidf_lr.pkl"))
    json.dump({"n": len(df), "n_event_groups": int(df.event_group.nunique())},
              open(os.path.join(REP, "tom_tat_baseline.json"), "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
