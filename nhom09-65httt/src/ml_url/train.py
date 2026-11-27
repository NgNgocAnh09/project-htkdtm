"""
TV3 - Bước 2: Huấn luyện và đánh giá mô hình phát hiện URL phishing.

Các mô hình:
  0. Luật đơn giản (rule-based)  -> mốc so sánh theo đề cương
  1. Logistic Regression          -> baseline ML
  2. Random Forest
  3. XGBoost (tinh chỉnh bằng Optuna, GroupKFold theo domain trên tập train)
  4. LightGBM

Chỉ số: PR-AUC, ROC-AUC, Precision, Recall, F1, FPR, ma trận nhầm lẫn.
Chạy: python ml_url/train.py
"""
import json
import os
import warnings

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import optuna
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_recall_curve, precision_score, recall_score,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from url_features import FEATURE_NAMES, extract_features

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "ml_url")
MODEL_DIR = os.path.join(BASE, "models")
REP = os.path.join(BASE, "reports", "ml_url")
SEED = 42
THRESHOLD = 0.5


def featurize(df):
    X = pd.DataFrame([extract_features(u) for u in df["url_defanged"]])[FEATURE_NAMES]
    return X.astype(float)


def rule_score(X):
    """Luật đơn giản: đếm số dấu hiệu đỏ, chia cho tổng số luật -> điểm 0..1"""
    flags = [
        X["has_ip_address"] > 0, X["is_shortened"] > 0, X["brand_not_in_domain"] > 0,
        X["suspicious_keyword_count"] >= 1, X["risky_tld"] > 0, X["free_hosting"] > 0,
        X["subdomain_count"] >= 3, X["num_at"] > 0, X["has_punycode"] > 0, X["url_length"] > 100,
    ]
    return np.sum(flags, axis=0) / len(flags)


def metrics(y, score, thr):
    pred = (score >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "PR_AUC": round(average_precision_score(y, score), 4),
        "ROC_AUC": round(roc_auc_score(y, score), 4),
        "Precision": round(precision_score(y, pred, zero_division=0), 4),
        "Recall": round(recall_score(y, pred), 4),
        "F1": round(f1_score(y, pred), 4),
        "FPR": round(fp / (fp + tn), 4),
        "TP": int(tp), "FP": int(fp), "TN": int(tn), "FN": int(fn),
    }


def tune_xgb(X, y, groups, n_trials=25):
    cv = GroupKFold(n_splits=4)

    def objective(trial):
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", 200, 600, step=100),
            max_depth=trial.suggest_int("max_depth", 3, 9),
            learning_rate=trial.suggest_float("learning_rate", 0.02, 0.2, log=True),
            subsample=trial.suggest_float("subsample", 0.6, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
            min_child_weight=trial.suggest_int("min_child_weight", 1, 10),
        )
        scores = []
        for tr, va in cv.split(X, y, groups):
            m = XGBClassifier(**params, eval_metric="logloss", random_state=SEED, n_jobs=2)
            m.fit(X.iloc[tr], y.iloc[tr])
            scores.append(average_precision_score(y.iloc[va], m.predict_proba(X.iloc[va])[:, 1]))
        return np.mean(scores)

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED))
    study.optimize(objective, n_trials=n_trials)
    return study.best_params, study.best_value


def build_models(best_xgb):
    return {
        "Logistic Regression (baseline)": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=2000, random_state=SEED)),
        "Random Forest": RandomForestClassifier(
            n_estimators=400, min_samples_leaf=2, random_state=SEED, n_jobs=2),
        "XGBoost (Optuna)": XGBClassifier(
            **best_xgb, eval_metric="logloss", random_state=SEED, n_jobs=2),
        "LightGBM": LGBMClassifier(
            n_estimators=400, learning_rate=0.05, num_leaves=31, random_state=SEED, verbose=-1),
    }


def run_split(df, split_col, best_xgb, vn_X):
    tr, te = df[df[split_col] == "TRAIN"], df[df[split_col] == "TEST"]
    Xtr, Xte = tr[FEATURE_NAMES], te[FEATURE_NAMES]
    ytr, yte = tr["label"], te["label"]
    rows, scores, fitted = [], {}, {}

    s = rule_score(Xte)
    scores["Luật đơn giản (rule-based)"] = s
    rows.append({"Mô hình": "Luật đơn giản (rule-based)", **metrics(yte, s, 0.2), "FPR_VN": None})

    for name, m in build_models(best_xgb).items():
        m.fit(Xtr, ytr)
        s = m.predict_proba(Xte)[:, 1]
        scores[name], fitted[name] = s, m
        vn_fpr = float(np.mean(m.predict_proba(vn_X)[:, 1] >= THRESHOLD))
        rows.append({"Mô hình": name, **metrics(yte, s, THRESHOLD), "FPR_VN": round(vn_fpr, 4)})
    return pd.DataFrame(rows), scores, fitted, yte, te


def plot_curves(yte, scores, title, fname):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for name, s in scores.items():
        p, r, _ = precision_recall_curve(yte, s)
        ax[0].plot(r, p, label=f"{name} (AP={average_precision_score(yte, s):.3f})")
        fpr, tpr, _ = roc_curve(yte, s)
        ax[1].plot(fpr, tpr, label=f"{name} (AUC={roc_auc_score(yte, s):.3f})")
    ax[0].set(xlabel="Recall", ylabel="Precision", title="Đường PR")
    ax[1].plot([0, 1], [0, 1], "k--", lw=0.8)
    ax[1].set(xlabel="FPR", ylabel="TPR (Recall)", title="Đường ROC")
    for a in ax:
        a.legend(fontsize=7, loc="lower left" if a is ax[0] else "lower right")
        a.grid(alpha=0.3)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(os.path.join(REP, fname), dpi=150)
    plt.close(fig)


def plot_cm(yte, s, title, fname):
    cm = confusion_matrix(yte, (s >= THRESHOLD).astype(int))
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    ax.imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=13)
    ax.set_xticks([0, 1], ["Lành tính", "Phishing"])
    ax.set_yticks([0, 1], ["Lành tính", "Phishing"])
    ax.set(xlabel="Dự đoán", ylabel="Thực tế", title=title)
    fig.tight_layout()
    fig.savefig(os.path.join(REP, fname), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(REP, exist_ok=True)
    df = pd.read_csv(os.path.join(DATA, "url_labeled.csv"))
    vn = pd.read_csv(os.path.join(DATA, "url_vn_benign_eval.csv"))
    print("Trích đặc trưng...")
    df = pd.concat([df, featurize(df)], axis=1)
    vn_X = featurize(vn)
    df[["url_id", "reg_domain", "label", "split_domain", "split_time"] + FEATURE_NAMES].to_csv(
        os.path.join(DATA, "url_lexical_features.csv"), index=False, encoding="utf-8-sig")

    tr = df[df["split_domain"] == "TRAIN"]
    print("Tinh chỉnh XGBoost bằng Optuna (GroupKFold 4 fold theo domain)...")
    best_xgb, cv_ap = tune_xgb(tr[FEATURE_NAMES], tr["label"], tr["reg_domain"])
    print("  best params:", best_xgb, "| PR-AUC CV:", round(cv_ap, 4))

    results = {}
    for split_col, label in (("split_domain", "A_domain"), ("split_time", "B_time")):
        res, scores, fitted, yte, te = run_split(df, split_col, best_xgb, vn_X)
        results[label] = res
        print(f"\n=== Split {label} ===\n", res.to_string(index=False))
        res.to_csv(os.path.join(REP, f"ket_qua_split_{label}.csv"), index=False, encoding="utf-8-sig")
        plot_curves(yte, scores, f"Split {label}: tập kiểm thử tách theo "
                    + ("tên miền" if label == "A_domain" else "thời gian"), f"pr_roc_{label}.png")
        if label == "A_domain":
            best_name = res.iloc[1:].sort_values("PR_AUC", ascending=False)["Mô hình"].iloc[0]
            best_model = fitted[best_name]
            for name in ("Logistic Regression (baseline)", best_name):
                plot_cm(yte, scores[name], name, f"cm_{'baseline' if 'Logistic' in name else 'best'}.png")
            # lưu các URL dự đoán sai để phân tích lỗi
            te = te.assign(score=scores[best_name])
            err = te[((te.score >= THRESHOLD).astype(int)) != te.label]
            err[["url_id", "url_defanged", "source", "label", "score"]].sort_values("score").to_csv(
                os.path.join(REP, "loi_du_doan_split_A.csv"), index=False, encoding="utf-8-sig")

    # độ quan trọng đặc trưng của mô hình tốt nhất
    imp = getattr(best_model, "feature_importances_", None)
    if imp is not None:
        fi = pd.Series(imp, index=FEATURE_NAMES).sort_values()
        fi.to_csv(os.path.join(REP, "do_quan_trong_dac_trung.csv"), encoding="utf-8-sig")
        fig, ax = plt.subplots(figsize=(6, 7))
        fi.plot.barh(ax=ax, color="#3b6ea5")
        ax.set(title=f"Độ quan trọng đặc trưng - {best_name}")
        fig.tight_layout()
        fig.savefig(os.path.join(REP, "feature_importance.png"), dpi=150)
        plt.close(fig)

    # train lại mô hình tốt nhất trên toàn bộ dữ liệu (train + test split A) để bàn giao
    final = build_models(best_xgb)[best_name]
    final.fit(df[FEATURE_NAMES], df["label"])
    joblib.dump({"model": final, "features": FEATURE_NAMES, "threshold": THRESHOLD,
                 "model_name": best_name, "trained_on": "PhishTank (05-11/2026) + Tranco + Hannousse2021",
                 "version": "1.0"}, os.path.join(MODEL_DIR, "url_phishing_model.pkl"))
    with open(os.path.join(REP, "tom_tat.json"), "w", encoding="utf-8") as f:
        json.dump({"best_model": best_name, "xgb_params": best_xgb, "xgb_cv_pr_auc": round(cv_ap, 4),
                   "n_samples": int(len(df)), "n_vn_eval": int(len(vn))}, f, ensure_ascii=False, indent=2)
    print("\nMô hình bàn giao:", best_name, "-> models/url_phishing_model.pkl")


if __name__ == "__main__":
    main()
