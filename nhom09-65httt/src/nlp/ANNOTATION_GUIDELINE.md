# Hướng dẫn gán nhãn bài viết cảnh báo lừa đảo (TV2)

Người gán nhãn: Nguyễn Minh Phú – Nhóm 09, 65HTTT
Dữ liệu: 247 bài trong `data/processed/sample_articles_for_nlp_tv2.csv` (VietnamNet 200, Dân trí 29, VnExpress 18; đăng từ 04/09 đến 26/11/2026)
Kết quả: `data/nlp/articles_labeled.csv`, cột `label`

## 1. Vì sao không gán thẳng 25 kịch bản của Bộ Công an

- Danh mục 25 kịch bản (bảng `scam_categories`) mô tả các chiêu lừa **qua không gian mạng**, trong khi bài thu thập được chủ yếu là tin pháp luật nói chung: nhiều bài về đầu tư, nhà đất, tham ô, bạo lực…
- Nhãn `category_code` tự động có sẵn trong file gốc xếp 220/247 bài vào SCAM_02 (giả danh công an), sai với phần lớn nội dung.
- 247 bài chia cho 25 lớp thì mỗi lớp chỉ vài bài, nhiều lớp không có bài nào, nên không huấn luyện được.

Vì vậy nhóm gộp thành **10 nhóm thủ đoạn**. Mỗi nhóm có ghi các mã SCAM_xx tương ứng để TV4 vẫn liên kết được với bảng `scam_categories`.

## 2. Danh sách nhãn

| Mã | Nhãn | Khi nào gán | Mã SCAM liên quan |
|---|---|---|---|
| A | GIA_DANH_CO_QUAN | Kẻ gian giả danh công an, viện kiểm sát, quân đội, cơ quan nhà nước để đe dọa và chiếm đoạt; "bắt cóc online" | SCAM_02, 08, 12, 16, 18, 20 |
| B | DAU_TU_HUY_DONG_VON | Lừa đầu tư: sàn ảo, forex, tiền số, đa cấp, huy động vốn với lãi cao (Mr Pips, Shark Thủy, Sen Tài Thu…) | SCAM_05 |
| C | BAT_DONG_SAN_NHA_O | Lừa mua bán đất, nhà ở xã hội, "suất ngoại giao", làm giả giấy tờ nhà đất | (mới) |
| D | VAY_TIEN_NGAN_HANG_HUI | Lừa vay "đáo hạn ngân hàng", nhân viên ngân hàng chiếm đoạt tiền gửi, cho vay online, hụi | SCAM_03, 13 |
| E | LUA_DAO_QUA_MANG_XA_HOI | Lừa qua Facebook/TikTok/Telegram…: bán hàng/vé, tình cảm, việc nhẹ lương cao, livestream, kêu gọi quyên góp | SCAM_04, 09, 10, 11, 15, 22, 25 |
| F | GIA_BAC_SI_Y_TE | Giả bác sĩ, thẩm mỹ không phép, bán thuốc/thực phẩm chức năng | SCAM_21 |
| G | NHAN_CHAY_VIEC_CHAY_AN | "Nổ" quen biết lãnh đạo để nhận tiền chạy án, chạy việc, chạy thủ tục, chạy dự án | SCAM_19 |
| H | TAI_KHOAN_DU_LIEU_MA_DOC | Mua bán tài khoản ngân hàng, dữ liệu cá nhân, phát tán mã độc, đường dây rửa tiền qua tài khoản (hạ tầng phục vụ lừa đảo) | SCAM_06, 07, 23 |
| K | LUA_DAO_KHAC | Có hành vi lừa đảo chiếm đoạt nhưng không thuộc các nhóm trên | – |
| I | KHONG_PHAI_LUA_DAO | Bài không nói về thủ đoạn lừa đảo: bạo lực, trộm cướp, tin giả, trốn thuế, tham ô, ma túy… | – |

## 3. Quy tắc

1. Chỉ đọc tiêu đề và phần tóm tắt có trong dữ liệu, không suy đoán ngoài văn bản.
2. Mỗi bài gán **đúng 1 nhãn**, chọn theo **thủ đoạn chính** mà bài mô tả, không theo tội danh.
   - VD: "Shark Bình rửa tiền cho Mr Pips" thì gán B, vì bài nằm trong vụ lừa đầu tư.
3. Ưu tiên khi một bài có nhiều dấu hiệu: A > G > H > B > C > D > F > E > K.
   - VD: giả danh công an liên lạc qua Zalo thì gán A, không gán E.
4. Bài tổng hợp nhiều thủ đoạn (VD: "25 kịch bản lừa đảo") gán theo thủ đoạn được nêu đầu tiên hoặc nhấn mạnh nhất.
5. Bài tham ô, trốn thuế, mua bán hóa đơn, cưỡng đoạt, tống tiền đều gán **I**, vì đây không phải lừa nạn nhân tự nguyện giao tiền.
6. Bài trùng sự kiện giữa các báo vẫn gán nhãn bình thường. Khi đánh giá mô hình, các bài này được gom chung một nhóm (`event_group`) để không bị chia vào cả train và test.

## 4. Ví dụ

| Bài | Nhãn |
|---|---|
| Vợ chồng tìm mọi cách chuyển 700 triệu đồng cho kẻ giả danh công an | A |
| Phó Đức Nam bị đề nghị mức án chung thân | B |
| Khởi tố 37 người lừa bán "suất ngoại giao" nhà ở xã hội | C |
| Người phụ nữ lừa bạn hơn 5 tỷ đồng tiền đáo hạn ngân hàng | D |
| Sáu người đàn ông mất 633 triệu khi tìm dịch vụ gái gọi trên Telegram | E |
| Cơ sở thẩm mỹ thuê người giả bác sĩ | F |
| Tìm nạn nhân bị lừa "chạy" biên chế giáo viên | G |
| Mua bán 6.000 thông tin tài khoản ngân hàng chuyển cho nhóm tội phạm ở Campuchia | H |
| Nhóm tài xế tráo heo của công ty chăn nuôi, chiếm đoạt 2,7 tỷ | K |
| 16 thanh thiếu niên mang hung khí "diễu phố" bị khởi tố | I |

## 5. Hạn chế

Nhãn do một người gán nên chưa đo được độ đồng thuận giữa các người gán (Cohen's Kappa). Nếu có thời gian, cho một thành viên khác gán lại khoảng 50 bài ngẫu nhiên để tính Kappa.
