"""
TV2 - Bước 4: Tổng hợp đánh giá (baseline + PhoBERT), vẽ ma trận nhầm lẫn, phân tích lỗi,
đánh giá phần trích thực thể. Chạy sau train_baseline.py và train_phobert.py.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "nlp")
REP = os.path.join(BASE, "reports", "nlp")

SHORT = {
    "GIA_DANH_CO_QUAN": "A.Giả danh CQ", "DAU_TU_HUY_DONG_VON": "B.Đầu tư",
    "BAT_DONG_SAN_NHA_O": "C.BĐS/nhà ở", "VAY_TIEN_NGAN_HANG_HUI": "D.Vay/NH/hụi",
    "LUA_DAO_QUA_MANG_XA_HOI": "E.Qua MXH", "GIA_BAC_SI_Y_TE": "F.Giả bác sĩ",
    "NHAN_CHAY_VIEC_CHAY_AN": "G.Chạy việc/án", "TAI_KHOAN_DU_LIEU_MA_DOC": "H.TK/dữ liệu",
    "LUA_DAO_KHAC": "K.Lừa đảo khác", "KHONG_PHAI_LUA_DAO": "I.Không LĐ",
}


def main():
    df = pd.read_csv(os.path.join(DATA, "articles_labeled.csv"))
    folds = pd.read_csv(os.path.join(DATA, "cv_folds.csv"))
    base = pd.read_csv(os.path.join(REP, "du_doan_cv_baseline.csv"))
    pho = pd.read_csv(os.path.join(REP, "du_doan_cv_phobert.csv"))
    P = base.merge(pho[["article_id", "phobert"]], on="article_id").merge(folds, on="article_id")
    P = P.rename(columns={"phobert": "PhoBERT fine-tune"})
    models = ["Từ khóa (rule)", "TF-IDF + Logistic Regression", "TF-IDF + Linear SVM", "PhoBERT fine-tune"]

    rows = []
    for m in models:
        pf = [f1_score(P.label[P.fold == k], P[m][P.fold == k], average="macro") for k in range(5)]
        rows.append({"Mô hình": m,
                     "Macro-F1": round(f1_score(P.label, P[m], average="macro"), 4),
                     "Macro-F1 TB 5 fold": round(np.mean(pf), 4), "± độ lệch": round(np.std(pf), 4),
                     "Macro-Precision": round(classification_report(P.label, P[m], output_dict=True, zero_division=0)["macro avg"]["precision"], 4),
                     "Macro-Recall": round(classification_report(P.label, P[m], output_dict=True, zero_division=0)["macro avg"]["recall"], 4),
                     "Accuracy": round((P[m] == P.label).mean(), 4)})
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(REP, "so_sanh_mo_hinh.csv"), index=False, encoding="utf-8-sig")
    print(res.to_string(index=False))

    best = res.sort_values("Macro-F1", ascending=False)["Mô hình"].iloc[0]
    labels = list(SHORT.keys())
    per = []
    for m in ("TF-IDF + Logistic Regression", "PhoBERT fine-tune"):
        rep = classification_report(P.label, P[m], labels=labels, output_dict=True, zero_division=0)
        for l in labels:
            per.append({"Mô hình": m, "Nhóm": SHORT[l], "Precision": round(rep[l]["precision"], 3),
                        "Recall": round(rep[l]["recall"], 3), "F1": round(rep[l]["f1-score"], 3),
                        "Số bài": int(rep[l]["support"])})
    pd.DataFrame(per).to_csv(os.path.join(REP, "chi_so_tung_nhom.csv"), index=False, encoding="utf-8-sig")

    for m, fn in ((best, "cm_best.png"), ("TF-IDF + Logistic Regression", "cm_tfidf_lr.png")):
        cm = confusion_matrix(P.label, P[m], labels=labels)
        fig, ax = plt.subplots(figsize=(7.5, 6.3))
        ax.imshow(cm, cmap="Blues")
        for i in range(len(labels)):
            for j in range(len(labels)):
                if cm[i, j]:
                    ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=9,
                            color="white" if cm[i, j] > cm.max() / 2 else "black")
        ax.set_xticks(range(len(labels)), [SHORT[l] for l in labels], rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(len(labels)), [SHORT[l] for l in labels], fontsize=8)
        ax.set(xlabel="Dự đoán", ylabel="Nhãn thực tế", title=f"Ma trận nhầm lẫn – {m} (gộp 5 fold)")
        fig.tight_layout(); fig.savefig(os.path.join(REP, fn), dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    x = np.arange(len(models))
    ax.bar(x, res["Macro-F1 TB 5 fold"], yerr=res["± độ lệch"], color=["#9aa5b1", "#5b8db8", "#5b8db8", "#2f5f8a"], capsize=4)
    for i, v in enumerate(res["Macro-F1"]):
        ax.text(i, v + 0.05, f"{v:.3f}".replace(".", ","), ha="center", fontsize=9)
    ax.axhline(0.8, ls="--", color="#c0392b", lw=1); ax.text(3.45, 0.81, "mục tiêu 0,80", color="#c0392b", fontsize=8, ha="right")
    ax.set_xticks(x, ["Từ khóa", "TF-IDF+LR", "TF-IDF+SVM", "PhoBERT"]); ax.set_ylim(0, 1)
    ax.set(ylabel="Macro-F1", title="So sánh Macro-F1 (5-fold theo nhóm sự kiện)")
    fig.tight_layout(); fig.savefig(os.path.join(REP, "so_sanh_macro_f1.png"), dpi=150); plt.close(fig)

    err = P[P[best] != P.label].merge(df[["article_id", "title"]], on="article_id")
    err[["article_id", "title", "label", best]].rename(columns={best: "du_doan"}).to_csv(
        os.path.join(REP, "loi_du_doan.csv"), index=False, encoding="utf-8-sig")
    pairs = err.groupby(["label", best]).size().sort_values(ascending=False).head(8)
    print("\nCặp nhầm nhiều nhất:\n", pairs)

    ent = df[["to_chuc_bi_gia_mao", "kenh_lien_lac"]].fillna("")
    stat = {"Bài có trích được tổ chức bị giả mạo": int((ent.to_chuc_bi_gia_mao != "").sum()),
            "Bài có trích được kênh liên lạc": int((ent.kenh_lien_lac != "").sum())}
    ch = ent.kenh_lien_lac.str.split("; ").explode().loc[lambda s: s != ""].value_counts()
    org = ent.to_chuc_bi_gia_mao.str.split("; ").explode().loc[lambda s: s != ""].value_counts()
    pd.concat([org.rename("so_bai").to_frame().assign(loai="to_chuc_bi_gia_mao"),
               ch.rename("so_bai").to_frame().assign(loai="kenh_lien_lac")]).to_csv(
        os.path.join(REP, "thong_ke_thuc_the.csv"), encoding="utf-8-sig")
    print(stat, "\n", org, "\n", ch)


if __name__ == "__main__":
    main()
