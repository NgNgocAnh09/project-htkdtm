import os
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

PHISHTANK_SEARCH_URL = "https://phishtank.org/phish_search.php"
PHISHTANK_DATA_DUMP_URL = "http://data.phishtank.com/data/online-valid.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def clean_url_text(raw_text: str) -> str:
    """
    Tách chuỗi URL sạch từ ô chứa cả text 'added on Nov 26th 2026...'
    """
    if not raw_text:
        return ""
    # Tách trước cụm 'added on'
    parts = re.split(r'added\s+on', raw_text, flags=re.IGNORECASE)
    clean = parts[0].strip()
    return clean

def scrape_phishtank_search_pages(max_pages: int = 5, delay: float = 2.0) -> list:
    """
    Cào trực tiếp danh sách URL phishing mới nhất từ giao diện website PhishTank
    https://phishtank.org/phish_search.php?valid=y&active=y&page=0, 1, 2...
    """
    all_phish = []
    print(f"[*] Bắt đầu cào trực tiếp từ website PhishTank (Tối đa {max_pages} trang)...")
    
    for page in range(max_pages):
        params = {
            "valid": "y",
            "active": "y",
            "page": page
        }
        try:
            print(f"  [+] Đang tải trang {page + 1}/{max_pages}: {PHISHTANK_SEARCH_URL}?valid=y&active=y&page={page}")
            resp = requests.get(PHISHTANK_SEARCH_URL, headers=HEADERS, params=params, timeout=15)
            if resp.status_code != 200:
                print(f"  [-] Lỗi HTTP {resp.status_code} tại trang {page}")
                break
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find('table', {'class': 'data'})
            if not table:
                print("  [-] Không tìm thấy bảng dữ liệu.")
                break
                
            rows = table.find_all('tr')
            for row in rows[1:]: # bỏ header
                cols = row.find_all('td')
                if len(cols) >= 4:
                    phish_id = cols[0].get_text(strip=True)
                    url_raw_info = cols[1].get_text(strip=True)
                    url_clean = clean_url_text(url_raw_info)
                    submitted_by = cols[2].get_text(strip=True)
                    valid_status = cols[3].get_text(strip=True)
                    
                    if url_clean:
                        all_phish.append({
                            "phish_id": phish_id,
                            "url": url_clean,
                            "submitted_by": submitted_by,
                            "status": valid_status,
                            "crawl_source": "PHISHTANK_WEB_SCRAPE",
                            "crawled_at": datetime.now().isoformat()
                        })
                        
            time.sleep(delay)
        except Exception as e:
            print(f"  [-] Ngoại lệ khi cào trang {page}: {e}")
            break
            
    print(f"[✓] Hoàn thành cào web: Thu thập được {len(all_phish)} URLs phishing từ giao diện PhishTank.")
    return all_phish

def fetch_phishtank_online_valid_dump(output_csv_path: str, max_records: int = 15000) -> str:
    """
    Tải trực tiếp nguồn cấp dữ liệu chính thức online-valid.csv từ data.phishtank.com
    Stream file và lưu vào thư mục data/raw/
    """
    print(f"[*] Bắt đầu kết nối tải snapshot chính thức từ PhishTank: {PHISHTANK_DATA_DUMP_URL}")
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    
    req_headers = {
        "User-Agent": "phishtank/academic_research_nhom09_65httt"
    }
    
    resp = requests.get(PHISHTANK_DATA_DUMP_URL, headers=req_headers, stream=True, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"Không thể tải file từ PhishTank, HTTP Status: {resp.status_code}")
        
    line_count = 0
    with open(output_csv_path, 'w', encoding='utf-8') as f:
        for line in resp.iter_lines(decode_unicode=True):
            if line:
                f.write(line + '\n')
                line_count += 1
                if max_records and line_count > max_records:
                    break
                    
    print(f"[✓] Đã tải và lưu {line_count - 1} dòng dữ liệu PhishTank thô tại: {output_csv_path}")
    return output_csv_path

if __name__ == "__main__":
    # Test cào thử trang web
    items = scrape_phishtank_search_pages(max_pages=2, delay=1.0)
    if items:
        print("Mẫu 2 dòng cào web:", items[:2])
