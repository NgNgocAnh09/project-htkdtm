"""
TV3 - Bước 1: Xây bộ dữ liệu URL có nhãn (phishing = 1, lành tính = 0) và chia tập.

Nguồn:
  - Phishing : PhishTank online-valid.csv do TV1 thu thập (src/data/raw/phishtank/)
  - Lành tính: (a) Tranco top-1M (bản tải ngày 27/11/2026) -> URL trang chủ của domain uy tín
               (b) URL hợp lệ có đường dẫn đầy đủ từ bộ dữ liệu công khai của
                   Hannousse & Yahiouche (2021), CC BY 4.0 (huggingface: pirocheto/phishing-url)
  - Tập riêng để đo báo động nhầm trên URL Việt Nam: domain .vn trong Tranco (không dùng để train)

Chia tập:
  - Split A (chính): tách theo tên miền gốc (registered domain), 80/20, không domain nào nằm ở cả 2 tập
  - Split B (thời gian): phishing gửi trước 01/11/2026 -> train, từ 01/11/2026 -> test

Chạy: python ml_url/build_dataset.py --tranco /duong_dan/top-1m.csv
Toàn bộ xử lý là chuỗi văn bản, không truy cập bất kỳ URL nào.
"""
import argparse
import os
import random

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from url_features import defang, registered_domain

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw", "phishtank", "online-valid.csv")
HF_DIR = os.path.join(BASE, "data", "ml_url", "raw")
OUT = os.path.join(BASE, "data", "ml_url")
SEED = 42


def load_phishing():
    p = pd.read_csv(RAW)
    p = p.drop_duplicates("url")
    return pd.DataFrame({
        "url": p["url"],
        "label": 1,
        "source": "PhishTank",
        "time": pd.to_datetime(p["submission_time"], utc=True),
        "target_brand": p["target"],
    })


def load_benign_hf():
    d = pd.concat([pd.read_parquet(os.path.join(HF_DIR, f)) for f in ("hf_train.parquet", "hf_test.parquet")])
    d = d[d["status"] == "legitimate"].drop_duplicates("url")
    return pd.DataFrame({"url": d["url"], "label": 0, "source": "Hannousse2021_legit",
                         "time": pd.NaT, "target_brand": None})


def tranco_urls(domains, source, rng):
    rows = []
    for dm in domains:
        host = dm if rng.random() < 0.5 else "www." + dm
        rows.append({"url": f"https://{host}/", "label": 0, "source": source,
                     "time": pd.NaT, "target_brand": None})
    return pd.DataFrame(rows)


def main(tranco_path, n_tranco=2000, n_vn=800):
    rng = random.Random(SEED)
    t = pd.read_csv(tranco_path, header=None, names=["rank", "domain"])
    is_vn = t["domain"].str.endswith(".vn")
    # domain toàn cầu: lấy ngẫu nhiên trong top 100.000, bỏ đuôi .vn
    glob = t[(~is_vn) & (t["rank"] <= 100_000)].sample(n_tranco, random_state=SEED)["domain"]
    vn = t[is_vn].head(n_vn)["domain"]

    phish = load_phishing()
    benign = pd.concat([load_benign_hf(), tranco_urls(glob, "Tranco_top100k", rng)])
    df = pd.concat([phish, benign], ignore_index=True)
    df["reg_domain"] = df["url"].map(registered_domain)

    vn_df = tranco_urls(vn, "Tranco_vn", rng)
    vn_df["reg_domain"] = vn_df["url"].map(registered_domain)
    # bỏ các domain .vn đã có sẵn trong tập chính để tập .vn hoàn toàn độc lập
    vn_df = vn_df[~vn_df["reg_domain"].isin(df["reg_domain"])]
    df = df[~df["reg_domain"].isin(vn_df["reg_domain"])]

    # ---- Split A: theo domain ----
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    tr_idx, te_idx = next(gss.split(df, df["label"], groups=df["reg_domain"]))
    df["split_domain"] = "TRAIN"
    df.iloc[te_idx, df.columns.get_loc("split_domain")] = "TEST"

    # ---- Split B: theo thời gian (chỉ áp dụng cho phishing, lành tính giữ như split A) ----
    cut = pd.Timestamp("2026-11-01", tz="UTC")
    df["split_time"] = df["split_domain"]
    m = df["label"] == 1
    df.loc[m, "split_time"] = (df.loc[m, "time"] >= cut).map({True: "TEST", False: "TRAIN"})
    # đảm bảo test theo thời gian không chứa domain đã thấy khi train
    train_doms = set(df.loc[df["split_time"] == "TRAIN", "reg_domain"])
    leak = (df["split_time"] == "TEST") & df["reg_domain"].isin(train_doms)
    df.loc[leak, "split_time"] = "DROP"

    # lưu dạng đã che URL (defang) theo quy định an toàn của nhóm
    os.makedirs(OUT, exist_ok=True)
    for name, d in (("url_labeled.csv", df), ("url_vn_benign_eval.csv", vn_df)):
        d = d.copy()
        d.insert(0, "url_id", range(1, len(d) + 1))
        d["url_defanged"] = d["url"].map(defang)
        d.drop(columns=["url"]).to_csv(os.path.join(OUT, name), index=False, encoding="utf-8-sig")

    print("Tổng:", len(df), "| VN eval:", len(vn_df))
    print(df.groupby(["source", "label"]).size())
    print(df.groupby(["split_domain", "label"]).size())
    print(df.groupby(["split_time", "label"]).size())
    print("Domain trùng giữa train/test (split A):",
          len(set(df[df.split_domain == "TRAIN"].reg_domain) & set(df[df.split_domain == "TEST"].reg_domain)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tranco", required=True, help="file top-1m.csv tải từ https://tranco-list.eu")
    a = ap.parse_args()
    main(a.tranco)
