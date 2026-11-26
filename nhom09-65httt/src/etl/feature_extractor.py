import math
import re
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'banking', 'secure', 'update', 'account', 'auth',
    'wallet', 'signin', 'support', 'service', 'confirm', 'password', 'webscr'
]

SHORTENER_DOMAINS = {
    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly',
    'adf.ly', 'bit.do', 'shorte.st', 'cutt.ly'
}

def calculate_shannon_entropy(text: str) -> float:
    """
    Tính toán độ hỗn loạn Shannon Entropy của chuỗi ký tự.
    Chuỗi URL phishing thường có entropy cao do chèn chuỗi ngẫu nhiên.
    """
    if not text:
        return 0.0
    entropy = 0.0
    text_len = len(text)
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    for count in freq.values():
        p = count / text_len
        entropy -= p * math.log2(p)
    return round(entropy, 4)

def is_ip_address(domain: str) -> bool:
    """
    Kiểm tra tên miền có phải là địa chỉ IPv4 hay không
    """
    ipv4_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    return bool(re.match(ipv4_pattern, domain))

def extract_lexical_features(raw_url: str):
    """
    Trích xuất thuần túy đặc trưng chuỗi ký tự ngoại tuyến (0 HTTP Request)
    """
    # Nếu URL đã defang, tạm thời phục hồi dấu chấm để parse URL logic
    temp_url = raw_url.replace('[.]', '.')
    temp_url = re.sub(r'^hxxp://', 'http://', temp_url, flags=re.IGNORECASE)
    temp_url = re.sub(r'^hxxps://', 'https://', temp_url, flags=re.IGNORECASE)
    
    if not re.match(r'^[a-zA-Z]+://', temp_url):
        temp_url = 'http://' + temp_url
        
    parsed = urlparse(temp_url)
    domain = parsed.netloc.split(':')[0]
    
    url_len = len(raw_url)
    domain_len = len(domain)
    
    # Số subdomain
    domain_parts = [p for p in domain.split('.') if p]
    subdomain_count = max(0, len(domain_parts) - 2) if len(domain_parts) >= 2 else 0
    
    # Tỷ lệ ký tự đặc biệt (@, -, ?, =, %, &, ...)
    special_chars = re.findall(r'[@\-_?=%&;+~#]', raw_url)
    special_char_ratio = round(len(special_chars) / url_len, 4) if url_len > 0 else 0.0
    
    # Entropy score
    entropy = calculate_shannon_entropy(raw_url)
    
    # Check IP
    has_ip = is_ip_address(domain)
    
    # Check URL shortener
    is_short = domain.lower() in SHORTENER_DOMAINS
    
    # Suspicious keywords
    url_lower = raw_url.lower()
    keyword_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)
    
    return {
        "url_length": url_len,
        "domain_length": domain_len,
        "subdomain_count": subdomain_count,
        "special_char_ratio": special_char_ratio,
        "entropy_score": entropy,
        "has_ip_address": has_ip,
        "is_shortened": is_short,
        "suspicious_keyword_count": keyword_count
    }
