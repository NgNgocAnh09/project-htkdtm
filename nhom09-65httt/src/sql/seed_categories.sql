-- ====================================================================
-- DỮ LIỆU KHỞI TẠO DANH MỤC 25 KỊCH BẢN THỦ ĐOẠN LỪA ĐẢO NĂM 2026
-- NGUỒN: BỘ CÔNG AN VIỆT NAM (THÁNG 09/2026)
-- PHỤC VỤ GÁN NHÃN NLP (TV2) VÀ PHÂN TÍCH XU HƯỚNG BI (TV4)
-- ====================================================================

INSERT INTO scam_categories (category_code, category_name, description) VALUES
('SCAM_01', 'Lừa đảo Deepfake / DeepVoice', 'Sử dụng công nghệ AI tạo video cuộc gọi hoặc giọng nói người thân, lãnh đạo để vay tiền gấp.'),
('SCAM_02', 'Giả danh Cơ quan Công an, Viện kiểm sát, Tòa án', 'Gọi điện thông báo liên quan đường dây rửa tiền, buôn ma túy, yêu cầu chuyển tiền vào tài khoản an toàn để kiểm tra.'),
('SCAM_03', 'Giả danh Nhân viên Ngân hàng thông báo lỗi giao dịch', 'Yêu cầu cung cấp mã OTP, mật khẩu Internet Banking để xử lý tài khoản bị khóa hoặc hủy lệnh chuyển nhầm.'),
('SCAM_04', 'Lừa đảo Tuyển dụng làm Việc nhẹ lương cao / Cộng tác viên Online', 'Làm nhiệm vụ xem video, đánh giá sản phẩm Shopee/Lazada, nạp tiền nhận hoa hồng và bị chiếm đoạt tiền nạp.'),
('SCAM_05', 'Kêu gọi đầu tư Tài chính, Sàn Tiền ảo, Forex nhái', 'Dụ dỗ tham gia các sàn giao dịch cam kết lợi nhuận 30-50%/tháng, điều chỉnh thuật toán cho thắng ban đầu rồi khóa rút tiền.'),
('SCAM_06', 'Phát tán tin nhắn Brandname giả mạo (SMS Spoofing)', 'Sử dụng trạm BTS giả mạo gửi tin nhắn chứa link độc mạo danh ngân hàng hoặc nhà mạng.'),
('SCAM_07', 'Lừa đảo Cài đặt Ứng dụng Dịch vụ công giả mạo (C06, VNeID)', 'Hướng dẫn cài app mã độc đuôi .apk chứa trojan nhằm chiếm quyền điều khiển Accessibility Service trên Android.'),
('SCAM_08', 'Giả mạo Khóa SIM vì chưa chuẩn hóa thông tin thuê bao', 'Gọi điện tự xưng Cục Viễn thông dọa khóa thuê bao sau 2 giờ nếu không làm theo hướng dẫn hoặc cung cấp OTP.'),
('SCAM_09', 'Lừa đảo Tặng quà tri ân / Trúng thưởng giá trị cao', 'Thông báo trúng xe máy, sổ tiết kiệm, yêu cầu nộp trước thuế thu nhập cá nhân hoặc phí vận chuyển.'),
('SCAM_10', 'Bẫy Tình cảm qua Mạng xã hội (Romance Scam / Lợn đồ tể)', 'Xây dựng mối quan hệ tình cảm rồi rủ đầu tư vào dự án tiền ảo, gửi quà từ nước ngoài bị hải quan giữ.'),
('SCAM_11', 'Chiếm đoạt Quyền kiểm soát Tài khoản MXH (Hack nick)', 'Gửi link bình chọn ảnh, cuộc thi giả mạo chứa phishing URL để lấy cắp thông tin tài khoản Facebook/Zalo.'),
('SCAM_12', 'Giả danh Cán bộ Thuế hỗ trợ Hoàn thuế, Cập nhật thông tin', 'Ép người dân truy cập đường dẫn giả mạo tổng cục thuế cài ứng dụng giả mạo để chiếm đoạt tài khoản ngân hàng.'),
('SCAM_13', 'Lừa đảo Cho vay Tiền qua App trực tuyến với lãi suất cắt cổ', 'Quảng cáo vay nhanh không thế chấp nhưng thu phí giải ngân trước hoặc tự ý trừ nợ với lãi suất phi pháp.'),
('SCAM_14', 'Giả mạo Biên lai Chuyển tiền thành công (Fake Bill)', 'Mua hàng rồi gửi ảnh chụp màn hình giả đã chuyển khoản liên ngân hàng, giục gửi hàng trước.'),
('SCAM_15', 'Lừa đảo Chuyến bay Giải cứu / Vé máy bay giá rẻ', 'Lập fanpage nhái đại lý hàng không bán vé máy bay dịp lễ tết với giá rẻ bất thường rồi chặn liên lạc.'),
('SCAM_16', 'Bắt cóc ảo / Con đang cấp cứu ở bệnh viện', 'Gọi điện cho phụ huynh dọa con đang mổ cấp cứu yêu cầu chuyển viện phí gấp hàng chục triệu đồng.'),
('SCAM_17', 'Lừa đảo Lập bàn thờ, Xem bói online, Giải hạn tâm linh', 'Đánh vào tâm lý lo lắng, dọa gặp hạn nặng phải mua bùa chú hoặc làm lễ hàng chục triệu đồng.'),
('SCAM_18', 'Giả mạo Cơ quan Bảo hiểm Xã hội', 'Thông báo hưởng trợ cấp bảo hiểm thất nghiệp và gửi link độc yêu cầu điền thông tin thẻ ngân hàng.'),
('SCAM_19', 'Lừa đảo Thu hồi vốn treo / Nhận lại tiền bị lừa', 'Mạo danh công ty luật, an ninh mạng cam kết lấy lại tiền lừa đảo nếu nộp trước phí ủy quyền.'),
('SCAM_20', 'Giả danh Điện lực thông báo cắt điện', 'Yêu cầu thanh toán tiền điện qua cổng thanh toán giả mạo để lấy cắp thông tin thẻ tín dụng.'),
('SCAM_21', 'Mạo danh Bác sĩ / Bệnh viện bán thuốc giả, thực phẩm chức năng', 'Lấy danh nghĩa bác sĩ bệnh viện lớn bán thực phẩm chức năng không rõ nguồn gốc với giá trên trời.'),
('SCAM_22', 'Lừa đảo Đấu giá hàng hiệu tồn kho hải quan', 'Quảng cáo thanh lý tài sản hải quan tịch thu giá rẻ, yêu cầu đặt cọc giữ chỗ.'),
('SCAM_23', 'Lừa đảo Đổi điểm tích lũy nhà mạng / Tích điểm thẻ tín dụng', 'Gửi SMS dụ bấm vào link đổi điểm lấy quà tặng rồi chiếm quyền kiểm soát thẻ.'),
('SCAM_24', 'Lừa đảo Cho số lô, số đề bao trúng', 'Thu phí trước để cho số đề cam kết trúng thưởng 100%.'),
('SCAM_25', 'Lừa đảo Dịch vụ Visa, Du học, Xuất khẩu lao động', 'Thu tiền làm thủ tục đi nước ngoài nhưng dùng giấy tờ giả hoặc ôm tiền bỏ trốn.')
ON CONFLICT (category_code) DO NOTHING;

-- KHỞI TẠO MỘT SỐ TỔ CHỨC TIÊU BIỂU THƯỜNG BỊ MẠO DANH
INSERT INTO organizations (org_name, org_type) VALUES
('Bộ Công an', 'GOVERNMENT'),
('Tổng cục Thuế', 'GOVERNMENT'),
('Bảo hiểm Xã hội Việt Nam', 'GOVERNMENT'),
('Vietcombank', 'BANK'),
('Techcombank', 'BANK'),
('BIDV', 'BANK'),
('Viettel', 'TELECOM'),
('VNPT', 'TELECOM'),
('Shopee', 'ECOMMERCE'),
('Lazada', 'ECOMMERCE')
ON CONFLICT (org_name) DO NOTHING;
