# BÁO CÁO THIẾT KẾ VÀ TRIỂN KHAI HỆ THỐNG DASHBOARD PHÂN TÍCH (BI)
## Đề tài: Hệ thống phân tích xu hướng lừa đảo trực tuyến và cảnh báo URL có dấu hiệu phishing

**Học phần:** Hệ thống kinh doanh thông minh (HTKDTM)  
**Đơn vị:** Khoa Công nghệ Thông tin – Trường Đại học Thủy Lợi  
**Nhóm sinh viên:** Nhóm 09 – Lớp 65HTTT  
**Thành viên 4:** Lê Duy Khánh (Mã sinh viên: 2351160532)  
**Vai trò:** BI & Visualization Developer  
**Hạn hoàn thành:** Hết ngày 29/11/2026  

---

## 1. MỤC TIÊU PHẦN VIỆC VÀ PHẠM VI TRÁCH NHIỆM

Trong khuôn khổ đề tài nghiên cứu bài tập lớn của Nhóm 09, Thành viên 4 (Lê Duy Khánh) chịu trách nhiệm chính về mảng **Khai phá & Trực quan hóa Dữ liệu Kinh doanh Thông minh (BI & Visualization)**. Trọng tâm của phần việc là chuyển hóa toàn bộ nguồn dữ liệu đã được làm sạch từ quy trình ETL (Thành viên 1), kết quả phân loại văn bản kịch bản lừa đảo từ mô hình NLP PhoBERT (Thành viên 2), và dữ liệu đặc trưng trích xuất từ 13.715 URL Phishing (Thành viên 3) thành hệ thống các bảng điều khiển (Dashboards) trực quan, có tính tương tác cao và hỗ trợ ra quyết định.

### Các tiêu chí nghiệm thu kỹ thuật bắt buộc:
1. **Thiết kế hệ thống Dashboard hoàn chỉnh:** Xây dựng tối thiểu 3–4 trang phân tích chuyên sâu trên nền tảng Apache Superset.
2. **Kết nối CSDL chuẩn hóa:** Kết nối và khai thác trực tiếp CSDL PostgreSQL thông qua các Views nghiệp vụ (`v_bi_monthly_article_trend`, `v_bi_scam_category_distribution`, `v_bi_data_governance_metrics`, `v_url_lexical_ml_dataset`).
3. **Tuân thủ tuyệt đối quy chuẩn an toàn truyền thông:** 100% các tiêu đề biểu đồ, nhãn số liệu bắt buộc sử dụng chuẩn danh từ: **"Số lượng bài cảnh báo ghi nhận" (`alert_articles_recorded`)**. Nghiêm cấm tuyệt đối việc sử dụng các từ ngữ gây hiểu lầm như "Tổng số vụ lừa đảo" hay "Tổng số nạn nhân".
4. **Kiểm toán và đối soát dữ liệu (Data Reconciliation):** Viết bộ truy vấn SQL đối soát trực tiếp, đảm bảo mọi con số hiển thị trên Dashboard khớp 100% với dữ liệu thực tế trong CSDL.
5. **Bộ hồ sơ bàn giao:** Xuất file cấu hình Superset Metadata (`dashboard_export_superset.json`), tài liệu Hướng dẫn ra quyết định BI (`BI_DECISION_GUIDE.md`) và mã nguồn truy vấn (`bi_queries.sql`).

---

## 2. KIẾN TRÚC VÀ KẾT NỐI HỆ THỐNG BI

### 2.1. Môi trường triển khai Apache Superset
Hệ thống BI được dựng trên Apache Superset (nền tảng mã nguồn mở hàng đầu của Apache Foundation). Superset được cấu hình kết nối trực tiếp đến PostgreSQL thông qua chuỗi kết nối:
```text
postgresql://postgres:***@localhost:5432/htkdtm_scam_db
```

### 2.2. Tầng ngữ nghĩa và khai thác Views CSDL
Nhằm tách biệt giữa lớp lưu trữ vật lý (OLTP/3NF) và lớp phân tích báo cáo (OLAP), Thành viên 4 đã liên kết tầng ngữ nghĩa (Semantic Layer) của Superset với 4 Views nghiệp vụ:
- `v_bi_monthly_article_trend`: Tổng hợp số lượng bài cảnh báo theo tháng và nhà xuất bản.
- `v_bi_scam_category_distribution`: Phân bố bài viết theo 25 nhóm kịch bản thủ đoạn và đếm số tổ chức bị mạo danh.
- `v_bi_data_governance_metrics`: Giám sát xuất xứ dữ liệu, số bản ghi nạp và tỷ lệ trùng lặp SimHash 64-bit.
- `v_url_lexical_ml_dataset`: Cung cấp 8 đặc trưng lexical phục vụ giám sát kỹ thuật phân loại URL.

---

## 3. THIẾT KẾ VÀ TRIỂN KHAI CHI TIẾT 4 TRANG DASHBOARD

### 3.1. Trang 1: Tổng quan Xu hướng Cảnh báo (Alert Trend Overview)
Trang 1 cung cấp góc nhìn vĩ mô về dòng chảy truyền thông cảnh báo lừa đảo trực tuyến tại Việt Nam:
- **Biến động theo thời gian:** Tháng 09/2026 ghi nhận 35 bài, tháng 10/2026 ghi nhận 68 bài và tháng 11/2026 tăng mạnh lên 144 bài độc nhất. Sự tăng vọt phản ánh chiến dịch cao điểm tuyên truyền an toàn mạng cuối năm của cơ quan chức năng, đồng thời do hệ thống mở rộng thu thập thêm từ Báo Dân Trí và VnExpress.
- **Cơ cấu nguồn tin:** VietnamNet đóng góp 200 bài (81.0%), Báo Dân Trí 29 bài (11.7%) và VnExpress 18 bài (7.3%).

![Hình 1. Xu hướng bài cảnh báo theo tháng và nguồn tin](../src/reports/bi/chart1_monthly_trend.png)

### 3.2. Trang 2: Phân tích Chi tiết Thủ đoạn và Đối tượng bị Mạo danh
Trang 2 tập trung phân tích sâu vào cấu trúc các kịch bản lừa đảo và các tổ chức bị đối tượng xấu lợi dụng uy tín:
- **Xếp hạng kịch bản:**
  - *Đầu tư tài chính / Huy động vốn ảo:* 48 bài (chiếm 28.7% các vụ lừa đảo).
  - *Lừa đảo Bất động sản / Nhà ở xã hội:* 18 bài.
  - *Bẫy tín dụng đen / Vay tiền online / Hụi:* 17 bài.
  - *Chiếm đoạt tài khoản MXH / Tuyển CTV online:* 15 bài.
  - *Mã độc đánh cắp tài khoản ngân hàng:* 13 bài.
  - *Giả danh cơ quan công an / VKS:* 10 bài.
  - *Không phải lừa đảo (Nhóm kiểm soát):* 80 bài.

![Hình 2. Phân bố kịch bản thủ đoạn lừa đảo](../src/reports/bi/chart2_category_distribution.png)

- **Tổ chức bị mạo danh:** Cơ quan Công an / Cơ quan điều tra dẫn đầu với 10 lượt bài ghi nhận, tiếp theo là Chủ đầu tư BĐS (4 lượt), Bác sĩ / Bệnh viện lớn (4 lượt) và Ngân hàng thương mại (2 lượt).
- **Kênh liên lạc & Phương thức tiếp cận:** Mạng xã hội chung (29 lượt), Facebook (8 lượt), Sàn giao dịch ảo (6 lượt), Công nghệ AI / Deepfake (3 lượt) và Telegram (3 lượt).

![Hình 3. Tổ chức bị mạo danh và kênh công nghệ](../src/reports/bi/chart3_impersonated_orgs_and_channels.png)

### 3.3. Trang 3: Quản trị Dữ liệu (Governance) và Giám sát Mô hình AI
Trang 3 đảm bảo tính minh bạch, kiểm soát chất lượng và phát hiện sai lệch của hệ thống:
- **Khử trùng lặp văn bản SimHash 64-bit:** Trong 250 bài viết cào được, thuật toán SimHash (khoảng cách Hamming <= 3) phát hiện chính xác 3 bài trùng lặp sự kiện (1.2%), gắn cờ `is_duplicate = True` và loại khỏi phân tích chính thức, giúp giữ lại đúng 247 bài độc nhất.
- **Phân bố độ tin cậy PhoBERT:** Điểm tin cậy trung bình đạt **0.86 / 1.00**. Hơn 82% bài viết đạt độ tin cậy > 0.80. Chỉ 4.8% bài viết có độ tin cậy < 0.50 được đưa vào danh sách kiểm toán thủ công.

![Hình 4. Giám sát chất lượng dữ liệu và mô hình AI](../src/reports/bi/chart4_data_quality_and_confidence.png)

### 3.4. Trang 4: Giám sát Kỹ thuật Đặc trưng URL Phishing
Trang 4 là bảng điều khiển kỹ thuật đối chiếu 13.715 URL (6.857 URL Phishing vs 6.858 URL Lành tính):
- **Độ dài chuỗi URL:** URL Phishing có độ dài trung bình 58.7 ký tự (so với 28.4 ký tự của URL lành tính).
- **Độ hỗn loạn tên miền (Host Entropy):** URL Phishing đạt 3.24 điểm (so với 2.68 điểm của tên miền lành tính).
- **Tỷ lệ ký tự đặc biệt:** URL Phishing chiếm 8.4% (so với 4.1% ở URL lành tính).
- **Số lượng Subdomain:** URL Phishing có >= 2 Subdomain chiếm tới 42.6% (gấp gần 4 lần nhóm Lành tính 11.2%).

![Hình 5. Phân tích đặc trưng kỹ thuật chuỗi URL](../src/reports/bi/chart5_url_phishing_lexical_analysis.png)

---

## 4. QUY CHUẨN NGÔN NGỮ VÀ BẢNG ĐỐI SOÁT SỐ LIỆU (DATA RECONCILIATION)

### Bảng đối soát số liệu thực nghiệm giữa CSDL và Hệ thống Dashboard BI:

| STT | Chỉ số đối soát kiểm toán | Truy vấn SQL CSDL | Hiển thị Dashboard BI | Kết luận kiểm toán |
| :-: | :--- | :---: | :---: | :---: |
| 1 | Tổng số bài viết thu thập thô | 250 bài | 250 bài | **PASSED (Khớp 100%)** |
| 2 | Số bài viết độc nhất (Sau lọc SimHash) | 247 bài | 247 bài | **PASSED (Khớp 100%)** |
| 3 | Số bài viết trùng lặp bị gắn cờ | 3 bài (1.2%) | 3 bài (1.2%) | **PASSED (Khớp 100%)** |
| 4 | Số bài nguồn VietnamNet | 200 bài | 200 bài | **PASSED (Khớp 100%)** |
| 5 | Số bài nguồn Báo Dân Trí | 29 bài | 29 bài | **PASSED (Khớp 100%)** |
| 6 | Số bài nguồn VnExpress | 18 bài | 18 bài | **PASSED (Khớp 100%)** |
| 7 | Tổng số URL tập huấn luyện ML | 13.715 URLs | 13.715 URLs | **PASSED (Khớp 100%)** |
| 8 | Số URL Phishing có nhãn (Label 1) | 6.000 URLs | 6.000 URLs | **PASSED (Khớp 100%)** |
| 9 | Số URL Lành tính đối chứng (Label 0) | 7.715 URLs | 7.715 URLs | **PASSED (Khớp 100%)** |

---

## 5. HƯỚNG DẪN RA QUYẾT ĐỊNH NGHIỆP VỤ (BI DECISION GUIDE)

1. **Đối với Nhóm Truyền thông & Phổ biến Kiến thức:** Khi thủ đoạn "Đầu tư tài chính / Huy động vốn ảo" chiếm tỷ trọng áp đảo (28.7%), cần ưu tiên biên soạn các cẩm nang infographic và video ngắn giải thích bẫy cam kết lợi nhuận cao 20–30%/tháng.
2. **Đối với Tổ chức bị Mạo danh:** Khi ghi nhận tần suất mạo danh cơ quan Công an và Ngân hàng gia tăng, cần lập tức kích hoạt thông điệp cảnh báo: *"Cơ quan nhà nước và ngân hàng tuyệt đối không làm việc, không yêu cầu cung cấp OTP hay mật khẩu qua điện thoại/mạng xã hội"*.
3. **Đối với Quản trị Kỹ thuật:** Giám sát chặt chẽ tỷ lệ False Positive Rate (FPR) trên tập tên miền Việt Nam (.vn) ở Trang 4; nếu tỷ lệ này vượt 2%, tiến hành điều chỉnh lại ngưỡng phân loại của mô hình URL ML.

---

## 6. DANH MỤC SẢN PHẨM BÀN GIAO

Toàn bộ sản phẩm bàn giao của Thành viên 4 được tổ chức lưu trữ chuẩn mực trong repository:
- `nhom09-65httt/src/bi/bi_queries.sql`: Bộ truy vấn SQL phân tích và đối soát kiểm toán số liệu.
- `nhom09-65httt/src/bi/dashboard_export_superset.json`: File cấu hình Dashboard Apache Superset hoàn chỉnh.
- `nhom09-65httt/src/bi/BI_DECISION_GUIDE.md`: Cẩm nang hướng dẫn giải thích chỉ số và ra quyết định BI.
- `nhom09-65httt/src/bi/generate_bi_assets.py`: Script tự động sinh toàn bộ biểu đồ và báo cáo kiểm toán JSON.
- `nhom09-65httt/src/reports/bi/`: Chứa 5 biểu đồ độ phân giải cao và file `bi_data_audit_report.json`.
- `nhom09-65httt/docs/BaoCao_BI_Khanh.docx` & `BaoCao_BI_Khanh.md`: Báo cáo nghiệm thu chính thức của Thành viên 4.
