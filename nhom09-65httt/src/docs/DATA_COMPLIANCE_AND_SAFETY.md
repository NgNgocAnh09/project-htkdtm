# ĐÁNH GIÁ HỢP LỆ VÀ AN TOÀN DỮ LIỆU
## (DATA COMPLIANCE, ETHICS & SAFETY DOCUMENT)

**Dự án:** Hệ thống phân tích xu hướng lừa đảo trực tuyến và cảnh báo URL có dấu hiệu phishing  
**Đơn vị thực hiện:** Nhóm 09 - 65HTTT  
**Người phụ trách chính:** Thành viên 1 - Data Engineer & ETL Leader (Ngọc Ánh)  
**Ngày ban hành:** 26/11/2026  

---

## 1. MỤC TIÊU VÀ PHẠM VI
Tài liệu này xác lập các nguyên tắc pháp lý, đạo đức dữ liệu và biện pháp an toàn kỹ thuật cho toàn bộ chu trình ETL (Extract - Transform - Load), bao gồm hai luồng dữ liệu độc lập:
1. **Luồng A:** Dữ liệu bản tin, cảnh báo lừa đảo công khai từ các cơ quan báo chí và cổng thông tin chính thức tại Việt Nam.
2. **Luồng B:** Dữ liệu chuỗi URL từ bộ dữ liệu mở **PhiUSIIL Phishing URL Dataset**.

---

## 2. CHÍNH SÁCH BẢN QUYỀN & HỢP LỆ NGUỒN DỮ LIỆU

### 2.1. Nguồn Dữ liệu PhishTank (Nguồn B)
* **Xuất xứ:** Cơ sở dữ liệu chia sẻ URL Phishing cộng đồng do OpenDNS / Cisco điều hành qua cổng thông tin **https://phishtank.org/**.
* **Chính sách sử dụng (Developer Policy):**
  * PhishTank cung cấp nguồn dữ liệu mở phục vụ mục đích nghiên cứu, phi thương mại.
  * Các ứng dụng thu thập dữ liệu định danh User-Agent minh bạch (ví dụ: `phishtank/academic_research_nhom09_65httt`).
  * Khuyến cáo cập nhật dữ liệu định kỳ qua tệp snapshot `online-valid.csv` hoặc cào trực tiếp qua giao diện web `phish_search.php` với tần suất có kiểm soát (delay tối thiểu 1.5 - 2.0s).
* **Biện pháp tuân thủ:**
  * Toàn bộ các lô dữ liệu tải từ PhishTank đều được lưu trữ bản sao thô (Raw payload) tại `data/raw/phishtank/` và tính mã băm bất biến SHA-256 ghi nhận vào bảng `provenance_logs`.
  * Bộ dữ liệu Phishing từ PhishTank chỉ đại diện cho các trường hợp đã bị báo cáo và xác minh (Verified Phish), tuyệt đối không đồng nhất số lượng URL này với tổng số vụ phạm tội lừa đảo trên thực tế.

### 2.2. Nguồn Báo chí & Cổng thông tin Cảnh báo Việt Nam (Nguồn A)
* **Đối tượng thu thập:** Cổng Thông tin điện tử Bộ Công an (mps.gov.vn), Báo Nhân Dân, VietnamNet, Báo điện tử Chính phủ,... (các chuyên mục Cảnh báo, An ninh mạng, Pháp luật).
* **Quy tắc thu thập lịch sự (Polite Crawling Policy):**
  * Tôn trọng triệt để chỉ thị trong tệp `robots.txt` của từng website.
  * Giới hạn tần suất gọi request: Thiết lập delay tối thiểu `1.5 - 2.5 giây` giữa các lần tải trang; không chạy cào dữ liệu song song đa luồng gây quá tải máy chủ máy chủ nguồn.
  * Khai báo định danh `User-Agent` minh bạch dạng: `AntiScamResearchBot/1.0 (+http://project-htkdtm.local; academic research)`.
* **Bảo vệ quyền sở hữu trí tuệ:** Chỉ lưu trữ tiêu đề, nội dung tóm tắt/đã làm sạch, thời gian đăng và đường dẫn liên kết gốc (`original_url`) nhằm phục vụ đối soát và trích dẫn khoa học.

---

## 3. NGUYÊN TẮC AN TOÀN KỸ THUẬT DỮ LIỆU (SAFETY MEASURES)

### 3.1. Quy tắc Tuyệt đối Cấm Truy cập URL Đích (Zero-Live-Request Rule)
* **Rủi ro:** Các URL phishing có thể chứa mã độc (malware, drive-by download, credential harvester).
* **Biện pháp bắt buộc:** Toàn bộ hệ thống (ETL, ML URL của TV3, Web App của TV5) **tuyệt đối không gửi HTTP/HTTPS request tới các URL nghi vấn**. Mọi bước trích xuất đặc trưng (Lexical Features) chỉ thực hiện thuần túy trên phân tích chuỗi ký tự ngoại tuyến (offline string parsing).

### 3.2. Quy chuẩn Vô hiệu hóa URL (URL Defanging Standard)
* Toàn bộ các URL nghi vấn hoặc gắn nhãn Phishing khi được nạp vào Cơ sở dữ liệu PostgreSQL hoặc hiển thị lên giao diện Dashboard/Web App **bắt buộc phải được defang**:
  * Thay thế giao thức: `http://` $\rightarrow$ `hxxp://`, `https://` $\rightarrow$ `hxxps://`.
  * Thay thế dấu chấm phân tách tên miền: `.` $\rightarrow$ `[.]`.
  * Ví dụ: `https://secure-login.bank.com/auth` $\rightarrow$ `hxxps://secure-login[.]bank[.]com/auth`.
* Tuyệt đối không lưu trữ hoặc xuất ra giao diện các liên kết siêu văn bản có thể click trực tiếp (`<a>` tags hoặc Markdown hyperlinks có thể thực thi).

### 3.3. Bảo vệ Dữ liệu Định danh Cá nhân (PII Protection & Redaction)
* Trong các bài viết cảnh báo sự việc thực tế, tên các nạn nhân, số tài khoản cá nhân, số căn cước công dân hoặc số điện thoại phản ánh phải được làm mờ (Masking/Redaction) tự động trước khi ghi vào CSDL:
  * Số điện thoại: `0912345678` $\rightarrow$ `0912***678`.
  * Số tài khoản: `190345678912` $\rightarrow$ `1903***12`.
  * CCCD: `001201001234` $\rightarrow$ `0012***234`.

---

## 4. QUẢN TRỊ XUẤT XỨ DỮ LIỆU (DATA PROVENANCE)
* Mỗi lô dữ liệu nạp vào hệ thống đều được cấp một `log_id` định danh duy nhất (UUID) trong bảng `provenance_logs`.
* Tệp thô (Raw payload) được tính toán mã băm an toàn **SHA-256** ngay tại thời điểm tải về để đảm bảo tính bất biến, chống sửa đổi trái phép và phục vụ kiểm toán dữ liệu (Data Auditing).

---

## 5. CAM KẾT & PHÊ DUYỆT
Tài liệu này là căn cứ kỹ thuật bắt buộc áp dụng cho toàn bộ mã nguồn của Thành viên 1 và chuyển giao cho các thành viên còn lại trong nhóm dự án tuân thủ nghiêm ngặt.
