"""TV2 - Tiền xử lý văn bản tiếng Việt và trích thực thể (tổ chức bị giả mạo, kênh liên lạc)."""
import html
import re

from pyvi import ViTokenizer

STOPWORDS = set("""
và của là có được cho với các những một này đã đang sẽ thì mà để khi từ trong ra vào lên xuống
tại theo về như nhưng nên do bị vì rằng cũng còn rất nhiều đến người này đó ấy nay hơn sau trước
""".split())


def clean_text(s: str) -> str:
    s = str(s)
    for _ in range(3):  # dữ liệu crawl có chỗ bị escape 2 lần (&amp;apos;)
        s = html.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)                    # thẻ HTML
    s = re.sub(r"\((Dân trí|VietnamNet|VnExpress)\)\s*-?", " ", s, flags=re.I)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"[\"“”‘’'`]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize(s: str, remove_stop=True) -> str:
    """Tách từ bằng PyVi (vd: 'lừa đảo' -> 'lừa_đảo'), bỏ số, dấu câu, từ dừng."""
    t = ViTokenizer.tokenize(clean_text(s).lower())
    toks = [w for w in t.split() if re.search(r"[a-zà-ỹđ]", w)]
    if remove_stop:
        toks = [w for w in toks if w not in STOPWORDS]
    return " ".join(toks)


# ---------------- Trích thực thể dựa trên từ điển + biểu thức chính quy ----------------
ORG_PATTERNS = {
    "Công an / cơ quan điều tra": r"(công an|cán bộ điều tra|cơ quan điều tra|cảnh sát|viện kiểm sát|vks|tòa án)",
    "Quân đội": r"(quân đội|thiếu tướng|đại tá|cảnh sát cơ động)",
    "Cơ quan thuế": r"(cơ quan thuế|cán bộ thuế|tổng cục thuế|cục thuế)",
    "Bảo hiểm xã hội": r"(bảo hiểm xã hội|bhxh)",
    "Ngân hàng": r"(ngân hàng|vietcombank|techcombank|bidv|vietinbank|agribank|seabank|pvcombank|mb bank|vpbank)",
    "Bác sĩ / bệnh viện": r"(bác sĩ|bệnh viện|phòng khám|nhân viên y tế)",
    "Chủ đầu tư / doanh nghiệp BĐS": r"(chủ đầu tư|sở xây dựng|nhà ở xã hội)",
    "Giáo xứ / tổ chức tôn giáo": r"(giáo xứ|linh mục|nhà thờ|chùa)",
    "Nhà mạng": r"(viettel|vnpt|mobifone|nhà mạng|cục viễn thông)",
    "Sàn TMĐT": r"(shopee|lazada|tiki|tiktok shop)",
}
CHANNEL_PATTERNS = {
    "Mạng xã hội (chung)": r"mạng xã hội",
    "Facebook / Fanpage": r"(facebook|fanpage)",
    "Zalo": r"zalo",
    "Telegram": r"telegram",
    "TikTok": r"tiktok",
    "YouTube / livestream": r"(youtube|livestream|phát trực tiếp)",
    "Threads / Instagram": r"(threads|instagram)",
    "Điện thoại / SMS": r"(gọi điện|cuộc gọi|điện thoại|tin nhắn|sms)",
    "Ứng dụng / website": r"(ứng dụng|app |website|trang web|đường link|đường dẫn)",
    "Sàn giao dịch ảo": r"(sàn giao dịch|sàn chứng khoán|forex|tiền ảo|tiền số|tiền mã hóa|crypto)",
    "AI / Deepfake": r"(deepfake|deepvoice|trí tuệ nhân tạo|\bai\b)",
}
IMPERSONATE_CUE = r"(giả danh|mạo danh|đóng giả|giả làm|giả mạo|tự xưng|giả |dỏm|rởm)"


def extract_entities(text: str) -> dict:
    """
    Trả về:
      to_chuc_bi_gia_mao: tổ chức xuất hiện gần từ 'giả danh/mạo danh/giả…' (cửa sổ 6 từ)
      to_chuc_nhac_den  : tất cả tổ chức nhắc tới
      kenh_lien_lac     : kênh/phương tiện mà bài nêu
    """
    low = clean_text(text).lower()
    orgs, imper = [], []
    for name, pat in ORG_PATTERNS.items():
        for m in re.finditer(pat, low):
            if name not in orgs:
                orgs.append(name)
            window = low[max(0, m.start() - 40): m.start()]
            if re.search(IMPERSONATE_CUE, window) and name not in imper:
                imper.append(name)
    chans = [n for n, p in CHANNEL_PATTERNS.items() if re.search(p, low)]
    return {"to_chuc_bi_gia_mao": imper, "to_chuc_nhac_den": orgs, "kenh_lien_lac": chans}
