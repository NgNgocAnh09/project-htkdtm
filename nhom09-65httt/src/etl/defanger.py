import re
from urllib.parse import urlparse

def defang_url(url: str) -> str:
    """
    Vô hiệu hóa an toàn URL độc hại (URL Defanging Standard).
    Chuyển:
        http://domain.com/path  -> hxxp://domain[.]com/path
        https://domain.com/path -> hxxps://domain[.]com/path
        ftp://domain.com        -> fxp://domain[.]com
    """
    if not url or not isinstance(url, str):
        return ""
    
    clean_url = url.strip()
    
    # 1. Đổi schema an toàn
    clean_url = re.sub(r'^http://', 'hxxp://', clean_url, flags=re.IGNORECASE)
    clean_url = re.sub(r'^https://', 'hxxps://', clean_url, flags=re.IGNORECASE)
    clean_url = re.sub(r'^ftp://', 'fxp://', clean_url, flags=re.IGNORECASE)
    
    # 2. Tách domain để chỉ thay đổi dấu chấm domain hoặc toàn bộ dấu chấm
    # Để an toàn tối đa cho chuỗi URL, bọc tất cả dấu '.' thành '[.]'
    defanged = clean_url.replace('.', '[.]')
    
    return defanged

def refang_url_for_analysis(defanged_url: str) -> str:
    """
    Hàm nội bộ chỉ phục vụ việc trích xuất domain/lexical ngoại tuyến (không gọi HTTP request).
    """
    if not defanged_url:
        return ""
    refanged = defanged_url.replace('[.]', '.')
    refanged = re.sub(r'^hxxp://', 'http://', refanged, flags=re.IGNORECASE)
    refanged = re.sub(r'^hxxps://', 'https://', refanged, flags=re.IGNORECASE)
    return refanged

def extract_domain_and_tld(url: str):
    """
    Trích xuất tên miền và TLD từ URL mà không kích hoạt request mạng.
    """
    # Đảm bảo có prefix để urlparse hoạt động chính xác
    temp_url = url
    if '[.]' in temp_url:
        temp_url = refang_url_for_analysis(temp_url)
        
    if not re.match(r'^[a-zA-Z]+://', temp_url):
        temp_url = 'http://' + temp_url
        
    parsed = urlparse(temp_url)
    netloc = parsed.netloc.split(':')[0] # bỏ port nếu có
    
    parts = netloc.split('.')
    tld = parts[-1] if len(parts) > 1 else ""
    return netloc, tld
