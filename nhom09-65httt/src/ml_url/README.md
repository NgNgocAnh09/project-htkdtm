# TV3 – Mô hình phát hiện URL phishing (lexical, offline)

Người thực hiện: Trần Quang Thịnh – Nhóm 09, 65HTTT

## Cài đặt
```bash
pip install -r ml_url/requirements.txt
```

## Chạy lại từ đầu (đứng ở thư mục `src/`)
```bash
# 1. Tải Tranco top-1M tại https://tranco-list.eu (file top-1m.csv), rồi:
python ml_url/build_dataset.py --tranco duong_dan/top-1m.csv
# 2. Huấn luyện + đánh giá + xuất mô hình
python ml_url/train.py
# 3. Thử hàm suy luận
python ml_url/predict.py "hxxp://vietcombank-xacminh[.]top/login"
```

## Bàn giao cho TV5 (web app)
```python
import sys; sys.path.append("src/ml_url")
from predict import check_url
kq = check_url(url_nguoi_dung_nhap)
# kq["diem_nghi_ngo"]  -> 0..1
# kq["muc_do"]         -> "Thấp" / "Cần kiểm tra" / "Cao"
# kq["bang_chung"]     -> list các dấu hiệu ký tự
# kq["khuyen_cao"]     -> lời khuyên hiển thị
# kq["url_hien_thi"]   -> URL đã che (hxxp, [.]), không bấm được
```
Mô hình: `src/models/url_phishing_model.pkl` (LightGBM, 33 đặc trưng, ngưỡng 0,5).

## An toàn
Các file trong `ml_url/` không import `requests`, `socket`, `urllib.request`;
không phân giải DNS, không truy cập URL đích. Dữ liệu URL lưu ở dạng đã che.

## Kết quả chính (tập test tách theo tên miền)
| Mô hình | PR-AUC | Recall | Precision | FPR |
|---|---|---|---|---|
| Luật đơn giản | 0,658 | 0,251 | 0,964 | 0,006 |
| Logistic Regression (baseline) | 0,956 | 0,845 | 0,896 | 0,059 |
| LightGBM (bàn giao) | 0,979 | 0,907 | 0,942 | 0,033 |

Chi tiết xem `reports/ml_url/` và báo cáo Word trong `docs/`.
