# BẢNG NHẬT KÝ XUẤT XỨ DỮ LIỆU (DATA PROVENANCE LOG)
## DỰ ÁN: HỆ THỐNG PHÂN TÍCH XU HƯỚNG LỪA ĐẢO & CẢNH BÁO URL PHISHING

**Đơn vị thực hiện:** Nhóm 09 - 65HTTT  
**Người phụ trách Quản trị Dữ liệu & ETL:** Thành viên 1 - Ngọc Ánh  
**Thời điểm cập nhật:** 2026-11-26 15:53:03  

---

## 1. NGUYÊN TẮC QUẢN TRỊ XUẤT XỨ (DATA PROVENANCE POLICY)
Mọi tập dữ liệu đưa vào hệ thống đều được truy vết qua mã băm mật mã học **SHA-256** nhằm đảm bảo:
1. **Tính bất biến (Immutability):** Dữ liệu thô không bị can thiệp trái phép.
2. **Khả năng kiểm toán (Auditability):** Bất kỳ dự đoán AI nào của TV2 hoặc TV3 đều có thể truy ngược về dòng bản ghi nguồn.
3. **Tuân thủ chính sách nguồn:** Thu thập theo đúng Developer Guidelines của PhishTank và chính sách báo chí Việt Nam.

---

## 2. BẢNG NHẬT KÝ CHI TIẾT CÁC LÔ DỮ LIỆU (DATA INGESTION LOG)

| Log ID | Tên Nguồn Dữ Liệu | Loại Nguồn | Dung lượng | SHA-256 Checksum | Số bản ghi nạp | Giấy phép / Nguồn | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `LOG_001_PHISHTANK_RAW` | **PhishTank Verified Phish Feed** | Stream / Web Scrape | 1.09 MB | `9dfc30c40fdc4a6e2f409222f82420132e6a70dd5ca76896e45549fa4124fef6` | 6,000 URLs thô | PhishTank / OpenDNS (Research use) | **SUCCESS** |
| `LOG_002_URL_PROCESSED` | **URL Dataset (PhishTank + Benign)** | Processed CSV | 0.97 MB | `f378888fd5b4d4b78e14a78eb417a8313c0a80df0ea4a88aa0c0a327e3022975` | 6,000 URLs (Cân bằng 1:1) | PhishTank & Tranco Curated | **SUCCESS** |
| `LOG_003_NEWS_VN` | **Bản tin Cảnh báo Lừa đảo Việt Nam** | Curated Crawl | 0.16 MB | `d086395955afbb999388a0e83acf910d81afa0b36468365fd5a6a3a8a4a37574` | 10 bài cảnh báo (1 bài trùng SimHash) | Bộ Công an, VietnamNet, Dân Trí | **SUCCESS** |

---

## 3. CHI TIẾT TIỀN XỬ LÝ & BIẾN ĐỔI (TRANSFORMATION DETAILS)

### 3.1. Đối với Luồng B (URL Phishing - PhishTank & Benign)
* **Thu thập PhishTank:** Thu thập qua module `crawler_phishtank.py` (hỗ trợ cả data dump stream và cào trực tiếp qua `phish_search.php` với delay kiểm soát).
* **Phương thức vô hiệu hóa (Defanging):** 100% URL được thay thế `http://` $\rightarrow$ `hxxp://`, `https://` $\rightarrow$ `hxxps://`, `.` $\rightarrow$ `[.]`.
* **Phân bổ Train/Test:** Chia theo Domain gốc (Domain-based split: ~80% Train, ~20% Test) đảm bảo các domain trong tập Test không bao giờ xuất hiện trong tập Train, ngăn ngừa triệt để hiện tượng Data Leakage.
* **Đặc trưng đã trích xuất:** 8 đặc trưng Lexical thuần túy ký tự ngoại tuyến (0 HTTP Request).

### 3.2. Đối với Luồng A (Bản tin Cảnh báo - Báo chí Việt Nam)
* **Chuẩn hóa thời gian:** Đồng bộ song song múi giờ chuẩn quốc tế `UTC` và múi giờ địa phương `ICT (Asia/Ho_Chi_Minh, UTC+7)`.
* **Khử trùng lặp (Deduplication):** Sử dụng thuật toán SimHash 64-bit với 2-gram từ vựng. Hệ thống đã phát hiện và gắn cờ chính xác 01 bài viết sao chép nội dung (`is_duplicate = TRUE`, khoảng cách Hamming = 5 $\le$ ngưỡng 12).
* **Bảo vệ quyền riêng tư (PII):** 100% số điện thoại và tài khoản ngân hàng nạn nhân được làm mờ (Masking).

---

## 4. BÀN GIAO TIẾP THEO
* **Thành viên 2 (NLP Specialist):** Tiếp nhận `data/processed/sample_articles_for_nlp_tv2.csv` để gán nhãn 25 kịch bản.
* **Thành viên 3 (ML URL Specialist):** Tiếp nhận `data/processed/sample_urls_for_ml_tv3.csv` (dữ liệu PhishTank thực tế) để huấn luyện Random Forest / XGBoost baseline.
* **Thành viên 4 (BI Developer):** Sử dụng các file SQL `sql/init_schema.sql` và `sql/views_superset.sql` để kết nối Apache Superset.
