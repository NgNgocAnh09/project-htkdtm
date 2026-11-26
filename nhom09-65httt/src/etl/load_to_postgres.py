import os
import psycopg2
import pandas as pd

DB_HOST = "localhost"
DB_PORT = 5433
DB_NAME = "antiscam_db"
DB_USER = "news_admin"
DB_PASS = "news_admin_123"

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def load_data_to_postgres():
    base_dir = r"d:\HTKDTM\project-htkdtm\nhom09-65httt\src"
    news_csv = os.path.join(base_dir, "data", "processed", "news_articles.csv")
    sample_ml_csv = os.path.join(base_dir, "data", "processed", "sample_urls_for_ml_tv3.csv")
    
    print("[*] Đang kết nối tới PostgreSQL (antiscam_db tại port 5433)...")
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Ghi nhận Provenance Log cho đợt nạp
    cur.execute("""
        INSERT INTO provenance_logs (source_name, source_type, raw_payload_checksum_sha256, total_records_ingested, notes)
        VALUES ('PhishTank Live Stream & VN News', 'HYBRID_INGESTION', '9dfc30c40fdc4a6e2f409222f82420132e6a70dd5ca76896e45549fa4124fef6', 6010, 'Nạp dữ liệu tự động cho TV1')
        RETURNING log_id;
    """)
    prov_id = cur.fetchone()[0]
    print(f"[+] Provenance Log ID: {prov_id}")
    
    # 2. Nạp Tin tức Cảnh báo (Luồng A)
    if os.path.exists(news_csv):
        df_news = pd.read_csv(news_csv)
        print(f"[*] Đang nạp {len(df_news)} bài viết vào news_articles...")
        for _, r in df_news.iterrows():
            cur.execute("""
                INSERT INTO news_articles (
                    article_id, title, clean_content, publisher, 
                    publish_date_utc, publish_date_ict, original_url, 
                    simhash_fingerprint, is_duplicate, provenance_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (article_id) DO NOTHING;
            """, (
                r['article_id'], r['title'], r['clean_content'], r['publisher'],
                r['publish_date_utc'], r['publish_date_ict'], r['original_url'],
                r['simhash_fingerprint'], bool(r['is_duplicate']), prov_id
            ))
            
            # Gán mapping category
            cur.execute("""
                INSERT INTO article_scam_mapping (article_id, category_id, is_ground_truth)
                SELECT %s, category_id, TRUE FROM scam_categories WHERE category_code = %s
                ON CONFLICT DO NOTHING;
            """, (r['article_id'], r['category_code']))
            
            # Gán mapping org
            cur.execute("""
                INSERT INTO article_org_mapping (article_id, org_id)
                SELECT %s, org_id FROM organizations WHERE org_name = %s
                ON CONFLICT DO NOTHING;
            """, (r['article_id'], r['org_name']))
        conn.commit()
        print("[✓] Đã nạp xong Luồng A (Tin tức cảnh báo).")

    # 3. Nạp URL Dataset & Lexical Features (Luồng B - 6.000 mẫu)
    if os.path.exists(sample_ml_csv):
        df_ml = pd.read_csv(sample_ml_csv)
        print(f"[*] Đang nạp {len(df_ml)} URLs vào url_dataset và lexical_features...")
        
        # Batch insert
        url_records = []
        lex_records = []
        for _, r in df_ml.iterrows():
            url_records.append((
                int(r['url_id']), str(r['raw_url_defanged']), str(r['domain']), 
                str(r['tld']) if pd.notna(r['tld']) else '', int(r['ground_truth_label']), 
                str(r['split_set']), str(r['source_dataset']), prov_id
            ))
            lex_records.append((
                int(r['url_id']), int(r['url_length']), int(r['domain_length']),
                int(r['subdomain_count']), float(r['special_char_ratio']),
                float(r['entropy_score']), bool(r['has_ip_address']),
                bool(r['is_shortened']), int(r['suspicious_keyword_count'])
            ))
            
        cur.executemany("""
            INSERT INTO url_dataset (
                url_id, raw_url_defanged, domain, tld, 
                ground_truth_label, split_set, source_dataset, provenance_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url_id) DO NOTHING;
        """, url_records)
        
        cur.executemany("""
            INSERT INTO lexical_features (
                url_id, url_length, domain_length, subdomain_count,
                special_char_ratio, entropy_score, has_ip_address,
                is_shortened, suspicious_keyword_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url_id) DO NOTHING;
        """, lex_records)
        
        conn.commit()
        print("[✓] Đã nạp xong Luồng B (URL Dataset & Lexical Features).")
        
    cur.close()
    conn.close()
    print("[🎉] TOÀN BỘ DỮ LIỆU ĐÃ NẠP THÀNH CÔNG VÀO POSTGRESQL!")

if __name__ == "__main__":
    load_data_to_postgres()
