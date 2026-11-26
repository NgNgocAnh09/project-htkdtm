# TỪ ĐIỂN DỮ LIỆU (DATA DICTIONARY)
## HỆ THỐNG CƠ SỞ DỮ LIỆU CHUẨN HÓA 3NF (POSTGRESQL)

**Dự án:** Hệ thống phân tích xu hướng lừa đảo trực tuyến và cảnh báo URL phishing  
**Người thiết kế:** Thành viên 1 - Data Engineer & ETL Leader (Ngọc Ánh)  
**Phiên bản:** 1.0 (26/11/2026)  

---

## 1. BẢNG DÙNG CHUNG: QUẢN TRỊ XUẤT XỨ (DATA PROVENANCE)

### Bảng: `provenance_logs`
Lưu vết xuất xứ của mọi tệp dữ liệu, đảm bảo tính toàn vẹn và khả năng kiểm toán.

| Tên trường | Kiểu dữ liệu | Ràng buộc | Diễn giải |
| :--- | :--- | :--- | :--- |
| `log_id` | `UUID` | PK, Default `uuid_generate_v4()` | Mã định danh bản ghi nhật ký xuất xứ |
| `source_name` | `VARCHAR(150)` | NOT NULL | Tên nguồn dữ liệu (ví dụ: 'PhiUSIIL Phishing URL Dataset', 'Báo Dân Trí') |
| `source_type` | `VARCHAR(50)` | NOT NULL | Loại nguồn: `CSV_STATIC_DATASET`, `WEB_SCRAPING`, `API_FEED` |
| `fetch_timestamp` | `TIMESTAMPTZ` | DEFAULT `CURRENT_TIMESTAMP` | Thời điểm thu thập / nạp dữ liệu |
| `raw_payload_checksum_sha256` | `VARCHAR(64)` | NOT NULL | Mã băm SHA-256 của tệp thô để kiểm chứng tính bất biến |
| `total_records_ingested` | `INTEGER` | NOT NULL, >= 0 | Tổng số bản ghi thu thập / nạp thành công |
| `status` | `VARCHAR(20)` | DEFAULT `'SUCCESS'` | Trạng thái: `'SUCCESS'`, `'WARNING'`, `'FAILED'` |
| `notes` | `TEXT` | NULL | Ghi chú bổ sung hoặc mô tả lỗi |

---

## 2. LUỒNG A: QUẢN LÝ BẢN TIN CẢNH BÁO LỪA ĐẢO

### Bảng: `scam_categories`
Danh mục 25 kịch bản / nhóm thủ đoạn lừa đảo trực tuyến (chuẩn hóa theo cảnh báo Bộ Công an 2026).

| Tên trường | Kiểu dữ liệu | Ràng buộc | Diễn giải |
| :--- | :--- | :--- | :--- |
| `category_id` | `SERIAL` | PK | Khóa chính tự tăng |
| `category_code` | `VARCHAR(50)` | UNIQUE, NOT NULL | Mã thủ đoạn (ví dụ: `SCAM_DEEPFAKE`, `SCAM_FINANCIAL_APP`) |
| `category_name` | `VARCHAR(255)` | NOT NULL | Tên nhóm thủ đoạn lừa đảo |
| `description` | `TEXT` | NULL | Mô tả kịch bản và dấu hiệu nhận biết |

### Bảng: `organizations`
Danh mục các cơ quan, doanh nghiệp, thương hiệu thường bị mạo danh.

| Tên trường | Kiểu dữ liệu | Ràng buộc | Diễn giải |
| :--- | :--- | :--- | :--- |
| `org_id` | `SERIAL` | PK | Khóa chính tự tăng |
| `org_name` | `VARCHAR(255)` | UNIQUE, NOT NULL | Tên tổ chức (ví dụ: 'Vietcombank', 'Cơ quan Công an', 'Shopee') |
| `org_type` | `VARCHAR(50)` | NOT NULL | Nhóm: `'BANK'`, `'GOVERNMENT'`, `'ECOMMERCE'`, `'TELECOM'` |

### Bảng: `news_articles`
Lưu trữ thông tin bài viết cảnh báo đã qua tiền xử lý, chuẩn hóa múi giờ và khử trùng lặp.

| Tên trường | Kiểu dữ liệu | Ràng buộc | Diễn giải |
| :--- | :--- | :--- | :--- |
| `article_id` | `UUID` | PK, Default `uuid_generate_v4()` | Mã định danh bài viết |
| `title` | `VARCHAR(500)` | NOT NULL | Tiêu đề bài viết cảnh báo |
| `clean_content` | `TEXT` | NOT NULL | Nội dung đã bóc tách HTML, chuẩn hóa ký tự và che mờ PII |
| `publisher` | `VARCHAR(100)` | NOT NULL | Cơ quan báo chí / website đăng tải |
| `publish_date_utc` | `TIMESTAMPTZ` | NOT NULL | Thời điểm xuất bản chuẩn UTC (ISO-8601) |
| `publish_date_ict` | `TIMESTAMPTZ` | NOT NULL | Thời điểm xuất bản múi giờ Việt Nam (UTC+7) |
| `original_url` | `TEXT` | NULL | Đường link bài báo gốc phục vụ đối soát |
| `simhash_fingerprint` | `VARCHAR(64)` | NULL | Mã băm SimHash 64-bit dùng để khử trùng nội dung |
| `is_duplicate` | `BOOLEAN` | DEFAULT `FALSE` | Cờ đánh dấu bài sao chép / trùng lặp |
| `duplicate_of_id` | `UUID` | FK $\rightarrow$ `news_articles(article_id)` | Trỏ tới bài viết gốc nếu bị trùng |
| `provenance_id` | `UUID` | FK $\rightarrow$ `provenance_logs(log_id)` | Khóa ngoại liên kết bản ghi nguồn gốc |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `CURRENT_TIMESTAMP` | Thời điểm nạp vào CSDL |

### Bảng: `article_scam_mapping` (Quan hệ N-N chuẩn 3NF)
Phục vụ việc một bài viết có thể đề cập đến nhiều thủ đoạn lừa đảo kết hợp.

| Tên trường | Kiểu dữ liệu | Ràng buộc | Diễn giải |
| :--- | :--- | :--- | :--- |
| `article_id` | `UUID` | PK, FK $\rightarrow$ `news_articles(article_id)` ON DELETE CASCADE | Mã bài viết |
| `category_id` | `INTEGER` | PK, FK $\rightarrow$ `scam_categories(category_id)` ON DELETE CASCADE | Mã thủ đoạn lừa đảo |
| `is_ground_truth` | `BOOLEAN` | DEFAULT `FALSE` | Đánh dấu nhãn do con người gán (True) hay dự đoán (False) |

### Bảng: `article_org_mapping` (Quan hệ N-N chuẩn 3NF)
Liên kết các tổ chức bị nhắc đến trong bài viết cảnh báo.

| Tên trường | Kiểu dữ liệu | Ràng buộc | Diễn giải |
| :--- | :--- | :--- | :--- |
| `article_id` | `UUID` | PK, FK $\rightarrow$ `news_articles(article_id)` ON DELETE CASCADE | Mã bài viết |
| `org_id` | `INTEGER` | PK, FK $\rightarrow$ `organizations(org_id)` ON DELETE CASCADE | Mã tổ chức bị giả mạo |

---

## 3. LUỒNG B: QUẢN LÝ TẬP DỮ LIỆU URL PHISHING (PHISHTANK & BENIGN DATASET)

### Bảng: `url_dataset`
Lưu trữ chuỗi URL đã qua xử lý an toàn (defanged), phân loại nhãn và nguồn gốc.

| Tên trường | Kiểu dữ liệu | Ràng buộc | Diễn giải |
| :--- | :--- | :--- | :--- |
| `url_id` | `BIGSERIAL` | PK | Khóa chính tự tăng |
| `raw_url_defanged` | `TEXT` | NOT NULL | Chuỗi URL an toàn (đã đổi `hxxp://` và `[.]`) |
| `domain` | `VARCHAR(255)` | NOT NULL | Tên miền trích xuất từ URL |
| `tld` | `VARCHAR(50)` | NULL | Phần mở rộng tên miền cao nhất (.com, .vn, .net,...) |
| `ground_truth_label` | `SMALLINT` | NOT NULL, CHECK in (0, 1) | Nhãn chuẩn: `0 = Benign` (Lành tính), `1 = Phishing` |
| `split_set` | `VARCHAR(10)` | DEFAULT `'TRAIN'` | Phân bổ tập: `'TRAIN'`, `'TEST'`, `'VAL'` (Domain-based split) |
| `source_dataset` | `VARCHAR(50)` | DEFAULT `'PhishTank'` | Tên nguồn dataset (`PhishTank` hoặc `Tranco_Curated`) |
| `provenance_id` | `UUID` | FK $\rightarrow$ `provenance_logs(log_id)` | Khóa ngoại trỏ nguồn nạp dữ liệu |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `CURRENT_TIMESTAMP` | Thời điểm nạp bản ghi |

### Bảng: `lexical_features`
Lưu trữ các đặc trưng ký tự ngoại tuyến (Lexical offline features) phục vụ Thành viên 3 huấn luyện mô hình ML.

| Tên trường | Kiểu dữ liệu | Ràng buộc | Diễn giải |
| :--- | :--- | :--- | :--- |
| `url_id` | `BIGINT` | PK, FK $\rightarrow$ `url_dataset(url_id)` ON DELETE CASCADE | Liên kết 1-1 với URL |
| `url_length` | `INTEGER` | >= 0 | Chiều dài toàn bộ chuỗi URL |
| `domain_length` | `INTEGER` | >= 0 | Chiều dài tên miền |
| `subdomain_count` | `INTEGER` | >= 0 | Số lượng tên miền con |
| `special_char_ratio` | `NUMERIC(6, 4)` | 0.0000 - 1.0000 | Tỷ lệ ký tự đặc biệt (@, -, ?, =, %,...) trong URL |
| `entropy_score` | `NUMERIC(6, 4)` | >= 0.0000 | Độ hỗn loạn Shannon Entropy của chuỗi URL |
| `has_ip_address` | `BOOLEAN` | DEFAULT `FALSE` | URL có sử dụng địa chỉ IP trực tiếp thay cho domain |
| `is_shortened` | `BOOLEAN` | DEFAULT `FALSE` | URL có dùng dịch vụ rút gọn (bit.ly, tinyurl,...) |
| `suspicious_keyword_count` | `INTEGER` | DEFAULT 0 | Số từ khóa đáng ngờ (login, verify, secure, banking,...) |

### Bảng: `label_versions`
Quản lý lịch sử và phiên bản gán nhãn dữ liệu qua các đợt cập nhật.

| Tên trường | Kiểu dữ liệu | Ràng buộc | Diễn giải |
| :--- | :--- | :--- | :--- |
| `version_id` | `SERIAL` | PK | Khóa chính tự tăng |
| `version_tag` | `VARCHAR(50)` | NOT NULL, UNIQUE | Thẻ phiên bản (ví dụ: `V1.0_PHIUSIIL_BENCHMARK`) |
| `description` | `TEXT` | NOT NULL | Mô tả chi tiết đợt gán nhãn / cập nhật |
| `created_at` | `TIMESTAMPTZ` | DEFAULT `CURRENT_TIMESTAMP` | Thời điểm ban hành phiên bản |

---

## 4. QUY TẮC TOÀN VẸN VÀ CHUẨN HÓA 3NF
1. **Chuẩn 1NF:** Tất cả các thuộc tính đều mang giá trị nguyên tử (Atomic). Không lưu mảng danh sách hay chuỗi phân tách bằng dấu phẩy trong cột.
2. **Chuẩn 2NF:** Loại bỏ phụ thuộc bộ phận; các bảng quan hệ N-N (`article_scam_mapping`, `article_org_mapping`) có khóa chính kết hợp và phụ thuộc hoàn toàn vào khóa chính.
3. **Chuẩn 3NF:** Tách biệt danh mục `scam_categories` và `organizations` khỏi bảng `news_articles`, loại bỏ phụ thuộc bắc cầu; tách bảng `lexical_features` khỏi `url_dataset` để tối ưu hóa truy vấn dung lượng nhẹ khi chỉ cần danh sách URL.
