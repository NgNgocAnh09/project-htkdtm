"""
TV3 - Hàm suy luận bàn giao cho TV5 (web app tra cứu URL).

Cách dùng:
    from predict import check_url
    kq = check_url("hxxp://vietcombank-xacminh[.]top/login")
    print(kq)

Hoặc chạy dòng lệnh:
    python ml_url/predict.py "http://vi-du[.]xyz/login"

AN TOÀN: hàm chỉ phân tích chuỗi ký tự của URL. Không gửi HTTP request,
không phân giải DNS, không mở trang đích. Kết quả là MỨC NGHI NGỜ để
tham khảo, không phải kết luận chắc chắn URL an toàn hay lừa đảo.
"""
import os
import sys

import joblib
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from url_features import defang, explain, extract_features  # noqa: E402

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "models", "url_phishing_model.pkl")
_bundle = None


def _load():
    global _bundle
    if _bundle is None:
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def check_url(url: str) -> dict:
    """
    Trả về:
      url_hien_thi : URL đã che (hxxp, [.]) để hiển thị, không bấm được
      diem_nghi_ngo: xác suất phishing theo mô hình (0..1)
      muc_do       : "Thấp" (<0.3) / "Cần kiểm tra" (0.3–0.7) / "Cao" (>=0.7)
      bang_chung   : danh sách dấu hiệu ký tự tìm thấy trong URL
      khuyen_cao   : lời khuyên kiểm tra thêm
      dac_trung    : giá trị đặc trưng đã trích (để debug / hiển thị chi tiết)
    """
    b = _load()
    f = extract_features(url)
    X = pd.DataFrame([f])[b["features"]].astype(float)
    p = float(b["model"].predict_proba(X)[:, 1][0])

    if p >= 0.7:
        muc = "Cao"
        kc = ("URL có nhiều dấu hiệu giống trang lừa đảo. Không nhập mật khẩu, OTP, thông tin thẻ. "
              "Hãy tự gõ địa chỉ chính thức của tổ chức hoặc tra cứu tại canhbao.khonggianmang.vn.")
    elif p >= 0.3:
        muc = "Cần kiểm tra"
        kc = ("Chưa đủ cơ sở kết luận. Nên kiểm tra kỹ tên miền, nguồn gửi link "
              "và đối chiếu với kênh chính thức trước khi truy cập.")
    else:
        muc = "Thấp"
        kc = ("Ít dấu hiệu nghi ngờ trong chuỗi URL, nhưng mô hình vẫn có thể bỏ sót. "
              "Vẫn cần cảnh giác nếu trang yêu cầu đăng nhập hoặc chuyển tiền.")

    return {
        "url_hien_thi": defang(url.replace("[.]", ".")),
        "diem_nghi_ngo": round(p, 4),
        "muc_do": muc,
        "bang_chung": explain(url, f),
        "khuyen_cao": kc,
        "mo_hinh": f"{b['model_name']} v{b['version']}",
        "dac_trung": f,
    }


if __name__ == "__main__":
    import json
    urls = sys.argv[1:] or [
        "hxxps://www[.]vietcombank[.]com[.]vn/",
        "hxxp://vietcombank-xacminh-taikhoan[.]top/login[.]php",
        "hxxps://allegrolokalnie[.]pl-oferta6664[.]cfd",
        "hxxps://github[.]com/oanhcuongdo/project-htkdtm",
    ]
    for u in urls:
        r = check_url(u)
        r.pop("dac_trung")
        print(json.dumps(r, ensure_ascii=False, indent=2))
