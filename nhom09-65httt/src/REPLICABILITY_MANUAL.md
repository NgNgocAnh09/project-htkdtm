# HƯỚNG DẪN TÁI LẬP HỆ THỐNG DỮ LIỆU & ETL
## (REPLICABILITY MANUAL - QUICK START GUIDE)

**Dự án:** Hệ thống phân tích xu hướng lừa đảo trực tuyến và cảnh báo URL phishing  
**Tác giả:** Thành viên 1 - Data Engineer & ETL Leader (Ngọc Ánh)  
**Ngày phát hành:** 26/11/2026  

---

## 1. YÊU CẦU HỆ THỐNG
* Hệ điều hành: Windows 10/11, Ubuntu 20.04+ hoặc macOS
* Python 3.10+ (Đã kiểm thử hoạt động chuẩn xác trên Python 3.12)
* PostgreSQL 14+ (Hoặc kết nối qua Docker Container)

---

## 2. CẤU TRÚC THƯ MỤC NGUỒN (`src/`)

```text
src/
├── data/
│   ├── raw/
│   │   └── phishtank/
│   │       └── online-valid.csv        # Snapshot dữ liệu PhishTank thô
│   └── processed/
│       ├── news_articles.csv           # Dữ liệu bài viết cảnh báo đã chuẩn hóa & khử trùng
│       ├── sample_articles_for_nlp_tv2.csv # Tệp bàn giao cho TV2 (NLP)
│       ├── url_dataset.csv             # 6,000 URLs đã defang an toàn & split Train/Test
│       ├── lexical_features.csv        # 8 đặc trưng lexical ngoại tuyến
│       └── sample_urls_for_ml_tv3.csv  # Tệp bàn giao hoàn chỉnh cho TV3 (ML)
├── docs/
│   ├── DATA_COMPLIANCE_AND_SAFETY.md   # Đánh giá hợp lệ & an toàn dữ liệu PhishTank
│   ├── DATA_DICTIONARY.md              # Từ điển dữ liệu CSDL chuẩn hóa 3NF
│   ├── ERD_SPECIFICATION.md            # Sơ đồ quan hệ thực thể (ERD Mermaid)
│   └── DATA_PROVENANCE_LOG.md          # Nhật ký xuất xứ dữ liệu & SHA-256
├── etl/
│   ├── defanger.py                     # Module vô hiệu hóa an toàn URL (hxxp://, [.])
│   ├── normalizer.py                   # Module chuẩn hóa múi giờ UTC & ICT
│   ├── deduplicator.py                 # Module khử trùng văn bản bằng SimHash 64-bit
│   ├── feature_extractor.py            # Trích xuất đặc trưng Lexical ngoại tuyến
│   ├── crawler_phishtank.py            # Cào / tải dữ liệu từ PhishTank
│   ├── benign_generator.py             # Sinh URL lành tính đối ứng từ Tranco
│   ├── etl_news.py                     # Pipeline Luồng A (Bản tin cảnh báo)
│   └── etl_phishtank.py                # Pipeline Luồng B (URL Dataset PhishTank)
├── sql/
│   ├── init_schema.sql                 # DDL khởi tạo bảng 3NF & Indexing
│   ├── seed_categories.sql             # Khởi tạo 25 kịch bản lừa đảo & tổ chức
│   └── views_superset.sql              # Views nghiệp vụ cho Superset (TV4) & ML (TV3)
└── REPLICABILITY_MANUAL.md             # Tài liệu này
```

---

## 3. CÁC BƯỚC TÁI LẬP TỪ ĐẦU (REPLICATION IN 3 STEPS)

### Bước 1: Cài đặt thư viện phụ thuộc
Mở terminal tại thư mục `src/` và chạy:
```bash
python -m pip install numpy pandas simhash psycopg2-binary requests beautifulsoup4 pytz
```

### Bước 2: Chạy Pipeline ETL tái tạo dữ liệu
Chạy lần lượt 2 pipeline ETL (Luồng A & Luồng B):
```bash
# 1. Chạy Luồng A (Bài viết, chuẩn hóa múi giờ, SimHash khử trùng lặp)
python etl/etl_news.py

# 2. Chạy Luồng B (Nạp PhiUSIIL, defanging, trích xuất lexical, Domain-based split)
python etl/etl_phiusiil.py
```
*Kết quả:* Hệ thống sẽ tự động tạo và làm sạch dữ liệu trong thư mục `data/processed/`.

### Bước 3: Khởi tạo Cơ sở dữ liệu PostgreSQL
Kết nối vào máy chủ PostgreSQL cục bộ hoặc qua pgAdmin/DBeaver, sau đó thực thi lần lượt 3 tệp SQL trong thư mục `sql/`:
1. `sql/init_schema.sql`: Khởi tạo cấu trúc bảng chuẩn hóa 3NF và các Index tối ưu hóa.
2. `sql/seed_categories.sql`: Nạp sẵn danh mục 25 kịch bản thủ đoạn của Bộ Công an 2026 và các tổ chức bị mạo danh.
3. `sql/views_superset.sql`: Tạo các View phục vụ kết nối trực quan hóa trên Apache Superset và trích xuất dữ liệu ML.

---

## 4. THÔNG TIN BÀN GIAO CHO CÁC THÀNH VIÊN TRONG NHÓM

### Bàn giao cho Thành viên 2 (AI / NLP Specialist):
* **Tệp dữ liệu:** `data/processed/sample_articles_for_nlp_tv2.csv`
* **Nhiệm vụ:** Tiến hành gán nhãn 25 kịch bản thủ đoạn (`category_code`) trên tập bài viết sạch đã được khử trùng lặp và phân tách nguồn.

### Bàn giao cho Thành viên 3 (Machine Learning URL Engineer):
* **Tệp dữ liệu:** `data/processed/sample_urls_for_ml_tv3.csv`
* **Nhiệm vụ:** Tập dữ liệu gồm 10.000 dòng đã được phân bổ sẵn cột `split_set` (TRAIN / TEST) theo Domain-based split để huấn luyện mô hình phân loại URL Phishing mà không bị rò rỉ dữ liệu. Các đặc trưng số học cơ bản đã được tính sẵn trong bảng `lexical_features`.

### Bàn giao cho Thành viên 4 (BI & Visualization Developer):
* **Tệp kết nối:** `sql/views_superset.sql`
* **Nhiệm vụ:** Kết nối Apache Superset trực tiếp vào 3 View:
  * `v_bi_monthly_article_trend`: Dựng biểu đồ xu hướng theo tháng.
  * `v_bi_scam_category_distribution`: Dựng biểu đồ phân bố 25 kịch bản thủ đoạn.
  * `v_bi_data_governance_metrics`: Dựng trang giám sát chất lượng và tỷ lệ trùng lặp dữ liệu.
