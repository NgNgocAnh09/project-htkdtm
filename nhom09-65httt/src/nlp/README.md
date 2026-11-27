# TV2 – Phân loại bài viết cảnh báo theo nhóm thủ đoạn lừa đảo (NLP)

Người thực hiện: Nguyễn Minh Phú – Nhóm 09, 65HTTT

## Cài đặt
```bash
pip install -r nlp/requirements.txt
# torch bản CPU: pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Chạy lại (đứng ở thư mục `src/`)
```bash
python nlp/train_baseline.py      # tạo data/nlp/articles_labeled.csv, chia fold, chạy baseline (vài giây)
python nlp/train_phobert.py --final   # fine-tune PhoBERT 5 fold + mô hình cuối (CPU khoảng 1 giờ)
python nlp/evaluate.py            # bảng so sánh, ma trận nhầm lẫn, phân tích lỗi, thống kê thực thể
```

## Bàn giao cho TV4 / TV5
```python
import sys; sys.path.append("src/nlp")
from predict import classify_article
kq = classify_article("Giả danh công an, ép nữ sinh thuê nhà nghỉ ... chuyển 300 triệu đồng")
# kq["nhom_thu_doan"], kq["do_tin_cay"], kq["ma_scam_lien_quan"],
# kq["to_chuc_bi_gia_mao"], kq["kenh_lien_lac"], kq["la_bai_lua_dao"]
```
Gán nhãn hàng loạt cho bảng tin tức để nạp vào PostgreSQL / Superset:
```bash
python nlp/predict.py --csv data/processed/news_articles.csv --out data/nlp/news_articles_predicted.csv
```
Mặc định hàm dùng TF-IDF + Logistic Regression (`models/nlp_tfidf_lr.pkl`), mô hình có Macro-F1
cao nhất khi đánh giá 5-fold, chạy nhẹ, không cần GPU. Muốn dùng PhoBERT đã fine-tune thì đặt
`NLP_MODEL=phobert` (cần torch, transformers và thư mục `models/phobert_scam_cls/`,
gửi kèm riêng vì nặng khoảng 270 MB).

## Tệp chính
| Tệp | Nội dung |
|---|---|
| `nlp/ANNOTATION_GUIDELINE.md` | Hướng dẫn gán nhãn, 10 nhóm thủ đoạn, ánh xạ sang SCAM_xx |
| `nlp/manual_labels.py` | Nhãn gán thủ công 247 bài |
| `nlp/text_utils.py` | Làm sạch, tách từ PyVi, trích thực thể (tổ chức bị giả mạo, kênh liên lạc) |
| `nlp/train_baseline.py` | Baseline từ khóa, TF-IDF + LR, TF-IDF + SVM |
| `nlp/train_phobert.py` | Fine-tune PhoBERT |
| `nlp/evaluate.py` | Đánh giá tổng hợp, biểu đồ |
| `nlp/predict.py` | Hàm suy luận |
| `data/nlp/articles_labeled.csv` | 247 bài đã gán nhãn |
| `reports/nlp/` | Kết quả, biểu đồ, danh sách lỗi |
