import os
import sys
import hashlib
import pandas as pd
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from crawler_phishtank import scrape_phishtank_search_pages, fetch_phishtank_online_valid_dump
from benign_generator import generate_benign_urls
from defanger import defang_url, extract_domain_and_tld
from feature_extractor import extract_lexical_features

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def run_phishtank_etl(
    raw_phishtank_csv: str,
    output_urls_path: str,
    output_features_path: str,
    output_ml_sample_path: str,
    target_sample_size: int = 5000
):
    """
    Pipeline ETL Luồng B chuyển dịch hoàn toàn sang PhishTank:
    1. Tải / Cào dữ liệu từ https://phishtank.org/
    2. Lưu bản sao thô (Raw payload) vào data/raw/phishtank/
    3. Tính mã băm SHA-256 ghi nhận Provenance
    4. Trích xuất URL Phishing hợp lệ từ PhishTank
    5. Tạo tập Benign URLs đối ứng từ các nguồn uy tín
    6. Vô hiệu hóa URL (Defanging: hxxp, [.])
    7. Trích xuất đặc trưng Lexical ngoại tuyến
    8. Chia Train/Test theo Domain gốc (Domain-based split)
    9. Xuất các file processed và sample cho ML Engineer (TV3)
    """
    print("==========================================================")
    print("  BẮT ĐẦU PIPELINE ETL LUỒNG B (NGUỒN DỮ LIỆU: PHISHTANK)")
    print("==========================================================")
    
    # Bước 1: Thu thập dữ liệu PhishTank
    if not os.path.exists(raw_phishtank_csv) or os.path.getsize(raw_phishtank_csv) == 0:
        print("[*] Tệp dữ liệu thô PhishTank chưa tồn tại. Đang tiến hành tải từ PhishTank...")
        try:
            fetch_phishtank_online_valid_dump(raw_phishtank_csv, max_records=target_sample_size * 2)
        except Exception as e:
            print(f"[!] Tải stream thất bại ({e}), chuyển sang cào trực tiếp qua Web Scraping...")
            scraped_items = scrape_phishtank_search_pages(max_pages=20, delay=1.5)
            df_scraped = pd.DataFrame(scraped_items)
            os.makedirs(os.path.dirname(raw_phishtank_csv), exist_ok=True)
            df_scraped.to_csv(raw_phishtank_csv, index=False, encoding='utf-8')
            
    checksum = compute_sha256(raw_phishtank_csv)
    print(f"[+] PhishTank Raw Data Checksum (SHA-256): {checksum}")
    
    # Bước 2: Đọc dữ liệu PhishTank thô
    df_raw = pd.read_csv(raw_phishtank_csv)
    print(f"[+] Tổng số bản ghi PhishTank đọc được: {len(df_raw)}")
    
    # Chuẩn hóa tên cột
    df_raw.columns = [c.strip().lower() for c in df_raw.columns]
    url_col = 'url' if 'url' in df_raw.columns else df_raw.columns[1]
    
    # Lấy danh sách URL phishing sạch
    phish_urls = df_raw[url_col].dropna().drop_duplicates().tolist()
    if len(phish_urls) > target_sample_size:
        phish_urls = phish_urls[:target_sample_size]
    print(f"[+] Số lượng URL Phishing chọn lọc: {len(phish_urls)}")
    
    # Bước 3: Tạo tập URL Lành tính (Benign) tương ứng 1:1
    benign_count = len(phish_urls)
    print(f"[*] Đang sinh {benign_count} URL lành tính từ các tên miền uy tín...")
    benign_urls = generate_benign_urls(count=benign_count, seed=42)
    
    # Bước 4: Defang, trích xuất Domain và Lexical Features
    print("[*] Đang tiến hành Defanging an toàn và trích xuất đặc trưng Lexical...")
    combined_data = []
    lexical_data = []
    
    # Nạp Phishing (Label = 1)
    for idx, u in enumerate(phish_urls):
        url_id = idx + 1
        defanged = defang_url(str(u))
        domain, tld = extract_domain_and_tld(str(u))
        lex = extract_lexical_features(defanged)
        
        combined_data.append({
            "url_id": url_id,
            "raw_url_defanged": defanged,
            "domain": domain,
            "tld": tld,
            "ground_truth_label": 1, # Phishing
            "source_dataset": "PhishTank",
            "provenance_checksum": checksum
        })
        lexical_data.append({"url_id": url_id, **lex})
        
    # Nạp Benign (Label = 0)
    offset = len(phish_urls)
    for idx, u in enumerate(benign_urls):
        url_id = offset + idx + 1
        defanged = defang_url(str(u))
        domain, tld = extract_domain_and_tld(str(u))
        lex = extract_lexical_features(defanged)
        
        combined_data.append({
            "url_id": url_id,
            "raw_url_defanged": defanged,
            "domain": domain,
            "tld": tld,
            "ground_truth_label": 0, # Benign
            "source_dataset": "Tranco_Curated",
            "provenance_checksum": checksum
        })
        lexical_data.append({"url_id": url_id, **lex})
        
    df_urls = pd.DataFrame(combined_data)
    df_lex = pd.DataFrame(lexical_data)
    
    # Bước 5: Chia Train/Test theo Domain (Domain-based split)
    print("[*] Thực hiện Domain-based Split (80% Train / 20% Test)...")
    unique_domains = df_urls['domain'].drop_duplicates().sample(frac=1.0, random_state=42).tolist()
    split_idx = int(len(unique_domains) * 0.8)
    train_domains = set(unique_domains[:split_idx])
    
    df_urls['split_set'] = df_urls['domain'].apply(lambda d: 'TRAIN' if d in train_domains else 'TEST')
    
    # Bước 6: Gộp và Xuất các sản phẩm bàn giao
    df_ml_sample = pd.merge(df_urls, df_lex, on='url_id')
    
    os.makedirs(os.path.dirname(output_urls_path), exist_ok=True)
    df_urls.to_csv(output_urls_path, index=False, encoding='utf-8')
    df_lex.to_csv(output_features_path, index=False, encoding='utf-8')
    df_ml_sample.to_csv(output_ml_sample_path, index=False, encoding='utf-8')
    
    print(f"[✓] Đã xuất {len(df_urls)} URLs defanged tới: {output_urls_path}")
    print(f"[✓] Đã xuất Lexical Features tới: {output_features_path}")
    print(f"[✓] Đã xuất Training Dataset hoàn chỉnh cho TV3 tại: {output_ml_sample_path}")
    print(f"    - Tổng số mẫu: {len(df_urls)} (50% Phishing từ PhishTank, 50% Benign)")
    print(f"    - Phân bổ Split Set: {df_urls['split_set'].value_counts().to_dict()}")
    print("==========================================================")
    return checksum, len(df_urls)

if __name__ == "__main__":
    base_dir = r"d:\HTKDTM\project-htkdtm\nhom09-65httt\src"
    raw_pt = os.path.join(base_dir, "data", "raw", "phishtank", "online-valid.csv")
    out_urls = os.path.join(base_dir, "data", "processed", "url_dataset.csv")
    out_lex = os.path.join(base_dir, "data", "processed", "lexical_features.csv")
    out_ml = os.path.join(base_dir, "data", "processed", "sample_urls_for_ml_tv3.csv")
    
    run_phishtank_etl(raw_pt, out_urls, out_lex, out_ml, target_sample_size=3000)
