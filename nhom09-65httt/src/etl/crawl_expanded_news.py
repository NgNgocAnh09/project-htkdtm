import os
import sys
import re
import uuid
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from normalizer import normalize_datetime
from deduplicator import SimHashDeduplicator

RSS_FEEDS = [
    ('VnExpress', 'https://vnexpress.net/rss/phap-luat.rss'),
    ('Báo Dân Trí', 'https://dantri.com.vn/rss/phap-luat.rss'),
    ('VietnamNet', 'https://vietnamnet.vn/rss/phap-luat.rss'),
    ('VnExpress Số Hóa', 'https://vnexpress.net/rss/so-hoa.rss'),
    ('Báo Dân Trí Công Nghệ', 'https://dantri.com.vn/rss/suc-manh-so.rss'),
    ('VietnamNet Thời Sự', 'https://vietnamnet.vn/rss/thoi-su.rss'),
    ('Báo Nhân Dân', 'https://nhandan.vn/rss/phap-luat-1209.rss'),
    ('Báo Tiền Phong', 'https://tienphong.vn/rss/phap-luat-12.rss')
]

KEYWORDS = [
    'lừa', 'chiếm đoạt', 'mạo danh', 'giả danh', 'tài khoản', 'mạng xã hội',
    'deepfake', 'ngân hàng', 'mã độc', 'tiền ảo', 'tin nhắn', 'cuộc gọi',
    'bắt cóc', 'vneid', 'thuế', 'đầu tư', 'app lừa', 'cộng tác viên', 'tín dụng'
]

# Ánh xạ từ khóa sang 25 kịch bản thủ đoạn của Bộ Công an
SCAM_MAPPING_RULES = [
    ('SCAM_01', ['deepfake', 'deepvoice', 'khuôn mặt', 'giọng nói']),
    ('SCAM_02', ['công an', 'viện kiểm sát', 'tòa án', 'rửa tiền', 'lệnh bắt']),
    ('SCAM_03', ['lỗi giao dịch', 'khóa tài khoản', 'hủy lệnh', 'mã otp']),
    ('SCAM_04', ['cộng tác viên', 'việc nhẹ', 'làm nhiệm vụ', 'hoa hồng', 'shopee', 'lazada']),
    ('SCAM_05', ['sàn ảo', 'tiền ảo', 'forex', 'đầu tư tài chính', 'lợi nhuận']),
    ('SCAM_06', ['brandname', 'tin nhắn sms', 'sms giả', 'bts']),
    ('SCAM_07', ['vneid', 'dịch vụ công', 'c06', 'định danh', 'cài app', 'file .apk']),
    ('SCAM_08', ['khóa sim', 'chuẩn hóa thuê bao', 'cục viễn thông']),
    ('SCAM_09', ['trúng thưởng', 'quà tri ân', 'xe máy', 'nộp thuế trước']),
    ('SCAM_10', ['romance', 'tình cảm', 'lợn đồ tể', 'quà nước ngoài']),
    ('SCAM_11', ['hack nick', 'chiếm quyền facebook', 'bình chọn']),
    ('SCAM_12', ['thuế', 'hoàn thuế', 'tổng cục thuế', 'quyết toán']),
    ('SCAM_13', ['vay tiền qua app', 'lãi suất', 'vay nhanh', 'phí giải ngân']),
    ('SCAM_14', ['fake bill', 'biên lai giả', 'chuyển nhầm tiền']),
    ('SCAM_15', ['vé máy bay', 'chuyến bay giải cứu', 'du lịch']),
    ('SCAM_16', ['bắt cóc', 'con đang cấp cứu', 'viện phí']),
    ('SCAM_17', ['xem bói', 'tâm linh', 'giải hạn', 'bùa']),
    ('SCAM_18', ['bảo hiểm xã hội', 'bhxh', 'thất nghiệp', 'thai sản']),
    ('SCAM_19', ['thu hồi vốn', 'lấy lại tiền', 'treo tiền']),
    ('SCAM_20', ['cắt điện', 'tiền điện', 'điện lực']),
    ('SCAM_21', ['thuốc giả', 'thực phẩm chức năng', 'bác sĩ bệnh viện']),
    ('SCAM_22', ['hàng hiệu', 'tồn kho', 'hải quan thanh lý']),
    ('SCAM_23', ['đổi điểm', 'tích điểm', 'thẻ tín dụng']),
    ('SCAM_24', ['số đề', 'số lô', 'bao trúng']),
    ('SCAM_25', ['visa', 'du học', 'xuất khẩu lao động'])
]

ORG_RULES = [
    ('Bộ Công an', ['công an', 'bộ công an', 'cảnh sát', 'c06']),
    ('Tổng cục Thuế', ['thuế', 'tổng cục thuế', 'chi cục thuế']),
    ('Bảo hiểm Xã hội Việt Nam', ['bảo hiểm xã hội', 'bhxh']),
    ('Vietcombank', ['vietcombank']),
    ('Techcombank', ['techcombank']),
    ('BIDV', ['bidv']),
    ('Viettel', ['viettel']),
    ('VNPT', ['vnpt', 'vinaphone']),
    ('Shopee', ['shopee']),
    ('Lazada', ['lazada'])
]

def infer_category_and_org(text: str):
    text_lower = text.lower()
    cat_code = 'SCAM_02' # Mặc định nếu k rõ
    for code, kws in SCAM_MAPPING_RULES:
        if any(kw in text_lower for kw in kws):
            cat_code = code
            break
            
    org_name = 'Bộ Công an'
    for org, kws in ORG_RULES:
        if any(kw in text_lower for kw in kws):
            org_name = org
            break
            
    return cat_code, org_name

def crawl_large_scale_news(max_articles: int = 250):
    """
    Cào hàng trăm bài cảnh báo từ RSS feeds chính thống,
    bóc tách tiêu đề, tóm tắt, nội dung, ngày đăng, publisher
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    raw_articles = []
    seen_titles = set()
    
    print("[*] Đang kết nối tới 8 kênh RSS feeds báo chí chính thống...")
    for publisher, feed_url in RSS_FEEDS:
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                root = ET.fromstring(resp.read())
                items = root.findall('.//item')
                print(f"  [+] {publisher}: Quét được {len(items)} tin.")
                for item in items:
                    title = item.find('title').text or ''
                    desc_raw = item.find('description').text or ''
                    link = item.find('link').text or ''
                    pub_date = item.find('pubDate').text or ''
                    
                    desc_text = BeautifulSoup(desc_raw, 'html.parser').get_text(strip=True)
                    full_text = f"{title}. {desc_text}".strip()
                    
                    # Kiểm tra chứa từ khóa lừa đảo
                    if any(kw in full_text.lower() for kw in KEYWORDS):
                        if title not in seen_titles:
                            seen_titles.add(title)
                            raw_articles.append({
                                "title": title,
                                "content": full_text,
                                "publisher": publisher,
                                "publish_date": pub_date,
                                "original_url": link
                            })
        except Exception as e:
            print(f"  [-] Lỗi đọc feed {publisher}: {e}")
            
    print(f"[✓] Đã thu thập được {len(raw_articles)} tin thô liên quan lừa đảo.")
    return raw_articles[:max_articles]

def process_and_save_expanded_news():
    """
    Chuẩn hóa thời gian, chạy SimHash 64-bit khử trùng lặp và lưu vào CSV
    """
    base_dir = r"d:\HTKDTM\project-htkdtm\nhom09-65httt\src"
    out_all_csv = os.path.join(base_dir, "data", "processed", "news_articles.csv")
    out_nlp_csv = os.path.join(base_dir, "data", "processed", "sample_articles_for_nlp_tv2.csv")
    
    raw_news = crawl_large_scale_news(max_articles=250)
    
    deduper = SimHashDeduplicator(f=64)
    processed_records = []
    stored_hashes = []
    
    duplicate_count = 0
    print("[*] Bắt đầu khử trùng SimHash và gán nhãn kịch bản...")
    
    for art in raw_news:
        art_id = str(uuid.uuid4())
        content = art["content"]
        
        # 1. Chuẩn hóa thời gian
        # Format RFC-822 từ RSS: 'Thu, 26 Nov 2026 09:17:14 +0700'
        dt_obj = None
        try:
            from email.utils import parsedate_to_datetime
            dt_obj = parsedate_to_datetime(art["publish_date"])
        except:
            dt_obj = datetime.now()
            
        dt_utc, dt_ict = normalize_datetime(dt_obj)
        
        # 2. Tính SimHash
        shash_int = deduper.build_simhash(content)
        shash_hex = hex(shash_int)
        
        # 3. Khử trùng lặp
        is_dup = False
        duplicate_of = None
        for prev_id, prev_hash in stored_hashes:
            dist = deduper.hamming_distance(shash_int, prev_hash)
            if dist <= 12: # Ngưỡng Hamming <= 12 là trùng
                is_dup = True
                duplicate_of = prev_id
                duplicate_count += 1
                break
                
        if not is_dup:
            stored_hashes.append((art_id, shash_int))
            
        cat_code, org_name = infer_category_and_org(content)
        
        # Che PII số điện thoại
        clean_content = re.sub(r'0\d{9,10}', '09***', content)
        
        processed_records.append({
            "article_id": art_id,
            "title": art["title"],
            "clean_content": clean_content,
            "publisher": art["publisher"],
            "publish_date_utc": dt_utc.isoformat(),
            "publish_date_ict": dt_ict.isoformat(),
            "original_url": art["original_url"],
            "simhash_fingerprint": shash_hex,
            "is_duplicate": is_dup,
            "duplicate_of_id": duplicate_of,
            "category_code": cat_code,
            "org_name": org_name
        })
        
    df_news = pd.DataFrame(processed_records)
    df_news.to_csv(out_all_csv, index=False, encoding='utf-8')
    
    # Xuất tệp sạch cho TV2 gán nhãn NLP (200-300 bài)
    df_nlp = df_news[df_news['is_duplicate'] == False][[
        'article_id', 'title', 'clean_content', 'publisher', 'publish_date_ict', 'category_code'
    ]].copy()
    df_nlp.to_csv(out_nlp_csv, index=False, encoding='utf-8')
    
    print("==========================================================")
    print(f"[✓] ĐÃ CÀO VÀ LƯU THÀNH CÔNG {len(df_news)} BÀI VIẾT CẢNH BÁO LỪA ĐẢO!")
    print(f"[+] Số bài viết trùng lặp bị SimHash phát hiện & gắn cờ: {duplicate_count}")
    print(f"[+] Số bài viết duy nhất bàn giao cho TV2 gán nhãn: {len(df_nlp)}")
    print(f"[+] Đường dẫn tệp lưu trữ: {out_all_csv}")
    print("==========================================================")
    return len(df_news)

if __name__ == "__main__":
    process_and_save_expanded_news()
