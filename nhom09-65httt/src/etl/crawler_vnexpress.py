import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def clean_vnexpress_date(raw_date_str: str) -> str:
    """
    Chuyển 'Thứ ba, 24/11/2026, 08:58 (GMT+7)' -> '2026-11-24 08:58:00'
    """
    if not raw_date_str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4}),?\s+(\d{1,2}):(\d{1,2})', raw_date_str)
    if match:
        d, m, y, h, minute = match.groups()
        return f"{y}-{int(m):02d}-{int(d):02d} {int(h):02d}:{int(minute):02d}:00"
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def crawl_vnexpress_article_detail(url: str):
    """
    Tải nội dung chi tiết bài viết VnExpress
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        
        title_el = soup.find('h1', class_='title-detail')
        title = title_el.get_text(strip=True) if title_el else ""
        
        date_el = soup.find('span', class_='date')
        date_str = clean_vnexpress_date(date_el.get_text(strip=True) if date_el else "")
        
        desc_el = soup.find('p', class_='description')
        desc = desc_el.get_text(strip=True) if desc_el else ""
        
        paras = soup.find_all('p', class_='Normal')
        body = ' '.join(p.get_text(strip=True) for p in paras if p.get_text(strip=True))
        
        if not body and desc:
            body = desc
            
        full_content = f"{desc}\n{body}".strip() if desc else body
        
        # Che PII số điện thoại nếu có
        full_content = re.sub(r'0\d{9,10}', '09***', full_content)
        
        if title and len(full_content) > 100:
            return {
                "title": title,
                "clean_content": full_content,
                "publisher": "VnExpress",
                "publish_date": date_str,
                "original_url": url
            }
    except Exception as e:
        print(f"[-] Lỗi tải bài {url}: {e}")
    return None

def crawl_vnexpress_scam_search(keywords=['lừa đảo', 'mạo danh ngân hàng', 'chiếm đoạt tài sản'], max_pages=3, delay=1.2):
    """
    Cào hàng loạt bài viết cảnh báo lừa đảo từ VnExpress Tìm kiếm
    """
    seen_urls = set()
    articles = []
    
    for kw in keywords:
        print(f"[*] Đang tìm kiếm từ khóa: '{kw}' trên VnExpress...")
        for page in range(1, max_pages + 1):
            search_url = f"https://timkiem.vnexpress.net/?q={requests.utils.quote(kw)}&page={page}"
            try:
                r = requests.get(search_url, headers=HEADERS, timeout=10)
                if r.status_code != 200:
                    break
                soup = BeautifulSoup(r.text, 'html.parser')
                news_items = soup.find_all('article', class_=re.compile(r'item-news'))
                if not news_items:
                    break
                
                print(f"  [+] Trang {page}: Tìm thấy {len(news_items)} kết quả.")
                for item in news_items:
                    h3 = item.find('h3')
                    if h3 and h3.find('a'):
                        link = h3.find('a')['href']
                        if link.startswith('https://vnexpress.net/') and link not in seen_urls and not link.endswith('.html#box_comment'):
                            seen_urls.add(link)
                            art = crawl_vnexpress_article_detail(link)
                            if art:
                                articles.append(art)
                                print(f"    -> Đã cào: {art['title'][:55]}...")
                            time.sleep(delay)
            except Exception as e:
                print(f"  [-] Ngoại lệ trang {page}: {e}")
                break
                
    print(f"[✓] Hoàn thành: Đã cào được tổng cộng {len(articles)} bài viết chi tiết từ VnExpress.")
    return articles

if __name__ == "__main__":
    arts = crawl_vnexpress_scam_search(keywords=['lừa đảo'], max_pages=2, delay=1.0)
    print("Tổng số bài cào được:", len(arts))
