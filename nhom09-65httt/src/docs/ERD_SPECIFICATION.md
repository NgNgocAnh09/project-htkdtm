# TÀI LIỆU SƠ ĐỒ QUAN HỆ THỰC THỂ (ERD SPECIFICATION)
## HỆ THỐNG CƠ SỞ DỮ LIỆU CHUẨN HÓA 3NF

**Dự án:** Phân tích xu hướng lừa đảo trực tuyến & cảnh báo URL Phishing  
**Thực hiện:** Thành viên 1 - Data Engineer & ETL Leader  
**Hệ quản trị CSDL:** PostgreSQL 15+  

---

## 1. SƠ ĐỒ QUAN HỆ THỰC THỂ DẠNG MERMAID

```mermaid
erDiagram
    PROVENANCE_LOGS ||--o{ NEWS_ARTICLES : "luu_xuat_xu"
    PROVENANCE_LOGS ||--o{ URL_DATASET : "luu_xuat_xu"

    SCAM_CATEGORIES ||--o{ ARTICLE_SCAM_MAPPING : "thuoc_ve"
    NEWS_ARTICLES ||--o{ ARTICLE_SCAM_MAPPING : "co_chu_de"

    ORGANIZATIONS ||--o{ ARTICLE_ORG_MAPPING : "bi_mao_danh"
    NEWS_ARTICLES ||--o{ ARTICLE_ORG_MAPPING : "nhac_den"

    NEWS_ARTICLES ||--o| NEWS_ARTICLES : "la_ban_sao_cua"

    URL_DATASET ||--|| LEXICAL_FEATURES : "chua_dac_trung"
    URL_DATASET ||--o{ LABEL_VERSIONS : "duoc_danh_phien_ban"

    PROVENANCE_LOGS {
        uuid log_id PK
        varchar source_name
        varchar source_type
        timestamptz fetch_timestamp
        varchar raw_payload_checksum_sha256
        integer total_records_ingested
        varchar status
        text notes
    }

    SCAM_CATEGORIES {
        serial category_id PK
        varchar category_code UK
        varchar category_name
        text description
    }

    ORGANIZATIONS {
        serial org_id PK
        varchar org_name UK
        varchar org_type
    }

    NEWS_ARTICLES {
        uuid article_id PK
        varchar title
        text clean_content
        varchar publisher
        timestamptz publish_date_utc
        timestamptz publish_date_ict
        text original_url
        varchar simhash_fingerprint
        boolean is_duplicate
        uuid duplicate_of_id FK
        uuid provenance_id FK
        timestamptz created_at
    }

    ARTICLE_SCAM_MAPPING {
        uuid article_id PK,FK
        integer category_id PK,FK
        boolean is_ground_truth
    }

    ARTICLE_ORG_MAPPING {
        uuid article_id PK,FK
        integer org_id PK,FK
    }

    URL_DATASET {
        bigserial url_id PK
        text raw_url_defanged
        varchar domain
        varchar tld
        smallint ground_truth_label
        varchar split_set
        varchar source_dataset
        uuid provenance_id FK
        timestamptz created_at
    }

    LEXICAL_FEATURES {
        bigint url_id PK,FK
        integer url_length
        integer domain_length
        integer subdomain_count
        numeric special_char_ratio
        numeric entropy_score
        boolean has_ip_address
        boolean is_shortened
        integer suspicious_keyword_count
    }

    LABEL_VERSIONS {
        serial version_id PK
        varchar version_tag UK
        text description
        timestamptz created_at
    }
```

---

## 2. PHÂN TÍCH RÕ RÀNG 2 LUỒNG DỮ LIỆU ĐỘC LẬP
Hệ thống thiết kế theo kiến trúc **Decoupled 2-Stream Data Architecture**:
* **Luồng A (Nội dung cảnh báo lừa đảo):** Xử lý văn bản, phục vụ NLP phân loại 25 kịch bản thủ đoạn (TV2) và trực quan hóa xu hướng truyền thông cảnh báo trên Superset (TV4).
* **Luồng B (Bộ dữ liệu URL Phishing):** Xử lý chuỗi URL tĩnh từ PhiUSIIL, phục vụ trích xuất đặc trưng Lexical và huấn luyện mô hình ML (TV3), cũng như tích hợp kiểm tra offline an toàn trên Web App (TV5).
* **Điểm nối duy nhất:** Bảng `provenance_logs` dùng chung để kiểm toán và truy vết nguồn gốc xuất xứ dữ liệu của cả 2 luồng.
