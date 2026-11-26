import random

# Danh sách top domain lành tính toàn cầu và Việt Nam được kiểm chứng uy tín (Tranco / Majestic)
TOP_BENIGN_DOMAINS = [
    # Cổng cơ quan chính phủ & tổ chức công Việt Nam
    "gov.vn", "chinhphu.vn", "mps.gov.vn", "baochinhphu.vn", "moit.gov.vn",
    "gdt.gov.vn", "bhxh.gov.vn", "monre.gov.vn", "mof.gov.vn", "mic.gov.vn",
    # Báo chí chính thống Việt Nam
    "vnexpress.net", "dantri.com.vn", "vietnamnet.vn", "nhandan.vn", "tuoitre.vn",
    "thanhnien.vn", "tienphong.vn", "laodong.vn", "vtv.vn", "vov.vn",
    # Ngân hàng & Thương mại điện tử uy tín tại Việt Nam
    "vietcombank.com.vn", "techcombank.com", "bidv.com.vn", "vietinbank.vn", "mbbank.com.vn",
    "shopee.vn", "lazada.vn", "tiki.vn", "sendo.vn", "thegioididong.com",
    # Dịch vụ công nghệ toàn cầu
    "google.com", "microsoft.com", "apple.com", "github.com", "wikipedia.org",
    "amazon.com", "cloudflare.com", "python.org", "apache.org", "mozilla.org",
    "stackoverflow.com", "linkedin.com", "youtube.com", "openai.com", "kaggle.com"
]

BENIGN_PATHS = [
    "", "/", "/about-us", "/contact", "/terms-and-conditions", "/privacy-policy",
    "/news/latest", "/products/view", "/help/faq", "/services", "/blog/post-101",
    "/documentation/guide", "/security/advisory", "/download/app", "/categories/tech"
]

def generate_benign_urls(count: int = 10000, seed: int = 42) -> list:
    """
    Sinh tập URL lành tính (Benign) có cấu trúc chuẩn mực từ các domain uy tín
    để tạo tập cân bằng nhãn 1:1 cho TV3 huấn luyện mô hình ML.
    """
    random.seed(seed)
    urls = []
    
    # 1. Sinh các URL cơ bản từ top domain
    for _ in range(count):
        domain = random.choice(TOP_BENIGN_DOMAINS)
        path = random.choice(BENIGN_PATHS)
        scheme = "https://" if random.random() > 0.1 else "http://"
        
        # Thỉnh thoảng có subdomain lành tính như mail, api, docs, m, news
        if random.random() > 0.6:
            sub = random.choice(["www", "api", "docs", "news", "m", "portal"])
            full_host = f"{sub}.{domain}"
        else:
            full_host = domain if domain.startswith("www.") else f"www.{domain}"
            
        # Thỉnh thoảng có query parameter thông thường
        if path and random.random() > 0.5:
            param = f"?page={random.randint(1, 10)}&lang=vi"
        else:
            param = ""
            
        full_url = f"{scheme}{full_host}{path}{param}"
        urls.append(full_url)
        
    return urls
