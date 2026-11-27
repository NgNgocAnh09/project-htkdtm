"""
TV3 - Trích xuất đặc trưng ký tự (lexical) từ chuỗi URL.

Nguyên tắc an toàn: module này CHỈ xử lý chuỗi văn bản.
Không import requests/urllib.request/socket, không phân giải DNS,
không truy cập URL đích.
"""
import math
import re
from collections import Counter
from urllib.parse import urlsplit

import tldextract

# Dùng bản Public Suffix List có sẵn trong thư viện, không tải từ mạng
_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())

SUSPICIOUS_KEYWORDS = [
    "login", "logon", "signin", "sign-in", "verify", "verification", "account",
    "update", "secure", "security", "banking", "bank", "confirm", "password",
    "wallet", "auth", "webscr", "billing", "payment", "invoice", "unlock",
    "suspend", "recover", "support", "service", "customer", "refund", "gift",
    "bonus", "free", "otp", "xacminh", "xacthuc", "dangnhap", "taikhoan", "nganhang",
]

# Các thương hiệu hay bị giả mạo (quốc tế + Việt Nam)
BRANDS = [
    "paypal", "apple", "icloud", "amazon", "microsoft", "office365", "outlook",
    "netflix", "facebook", "instagram", "whatsapp", "google", "allegro", "dhl",
    "fedex", "usps", "irs", "chase", "wellsfargo", "binance", "coinbase", "metamask",
    "vietcombank", "techcombank", "bidv", "vietinbank", "agribank", "mbbank",
    "tpbank", "vpbank", "acb", "sacombank", "shopee", "lazada", "tiki", "zalo",
    "momo", "viettel", "vnpt", "mobifone", "vneid", "dichvucong", "evn",
]

SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly",
    "adf.ly", "bit.do", "shorte.st", "cutt.ly", "rebrand.ly", "rb.gy", "t.ly",
    "s.id", "tiny.cc", "shorturl.at", "v.gd", "qrco.de",
}

# TLD giá rẻ hay xuất hiện trong danh sách phishing (tham khảo báo cáo của Spamhaus/Interisle)
RISKY_TLDS = {
    "cfd", "top", "xyz", "sbs", "icu", "click", "buzz", "shop", "online", "site",
    "live", "rest", "bond", "cyou", "monster", "fun", "life", "info", "pw", "tk",
    "ml", "ga", "cf", "gq", "work", "support", "vip", "win", "lat", "store", "best",
}

FREE_HOSTING = [
    "weebly", "wixsite", "000webhost", "firebaseapp", "web.app", "github.io",
    "netlify", "vercel", "pages.dev", "workers.dev", "blogspot", "glitch.me",
    "repl.co", "herokuapp", "hostgator", "sites.google", "ipfs", "r2.dev",
    "square.site", "godaddysites", "webflow", "framer",
]

FEATURE_NAMES = [
    "url_length", "host_length", "path_length", "query_length",
    "num_dots", "num_hyphens", "num_underscores", "num_slashes", "num_at",
    "num_qmark", "num_equal", "num_percent", "num_digits", "digit_ratio",
    "special_char_ratio", "subdomain_count", "host_digit_count", "host_hyphen_count",
    "has_ip_address", "is_shortened", "has_port", "has_punycode", "double_slash_in_path",
    "path_depth", "longest_token", "entropy_url", "entropy_host",
    "suspicious_keyword_count", "brand_not_in_domain", "risky_tld", "free_hosting",
    "has_file_ext", "has_www",
]

_IP_RE = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")


def refang(url: str) -> str:
    """Chuyển URL đã che (hxxp, [.]) về dạng chuỗi để phân tích. Chỉ xử lý text."""
    u = str(url).strip()
    u = u.replace("[.]", ".").replace("(.)", ".").replace("[:]", ":")
    u = re.sub(r"^hxxp", "http", u, flags=re.IGNORECASE)
    return u


def defang(url: str) -> str:
    """Che URL để lưu trữ / hiển thị an toàn (không bấm được)."""
    u = re.sub(r"^http", "hxxp", str(url), flags=re.IGNORECASE)
    return u.replace(".", "[.]")


def entropy(s: str) -> float:
    if not s:
        return 0.0
    n = len(s)
    return -sum(c / n * math.log2(c / n) for c in Counter(s).values())


def parse(url: str):
    u = refang(url)
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", u):
        u = "http://" + u
    try:
        sp = urlsplit(u)
        host = (sp.hostname or "").lower()
        port = sp.port if sp.netloc and ":" in sp.netloc.split("@")[-1] else None
    except ValueError:
        sp, host, port = urlsplit("http://invalid"), "", None
    return u, sp, host, port


def registered_domain(url: str) -> str:
    _, _, host, _ = parse(url)
    if _IP_RE.match(host):
        return host
    ext = _EXTRACT(host)
    return ext.top_domain_under_public_suffix or host


def extract_features(url: str) -> dict:
    u, sp, host, port = parse(url)
    path, query = sp.path or "", sp.query or ""
    low = u.lower()
    ext = _EXTRACT(host)
    reg = (ext.domain or "").lower()
    sub = (ext.subdomain or "").lower()
    is_ip = bool(_IP_RE.match(host))

    tokens = [t for t in re.split(r"[/\.\?=&\-_:]", low) if t]
    special = sum(1 for ch in u if not ch.isalnum())
    digits = sum(ch.isdigit() for ch in u)

    # thương hiệu xuất hiện trong URL nhưng không phải tên miền chính -> dấu hiệu giả mạo
    brand_hit = 0
    for b in BRANDS:
        if b in low and b != reg:
            brand_hit = 1
            break

    sub_parts = [p for p in sub.split(".") if p and p != "www"]

    f = {
        "url_length": len(u),
        "host_length": len(host),
        "path_length": len(path),
        "query_length": len(query),
        "num_dots": u.count("."),
        "num_hyphens": u.count("-"),
        "num_underscores": u.count("_"),
        "num_slashes": u.count("/"),
        "num_at": u.count("@"),
        "num_qmark": u.count("?"),
        "num_equal": u.count("="),
        "num_percent": u.count("%"),
        "num_digits": digits,
        "digit_ratio": round(digits / max(len(u), 1), 4),
        "special_char_ratio": round(special / max(len(u), 1), 4),
        "subdomain_count": 0 if is_ip else len(sub_parts),
        "host_digit_count": sum(ch.isdigit() for ch in host),
        "host_hyphen_count": host.count("-"),
        "has_ip_address": int(is_ip),
        "is_shortened": int(host.removeprefix("www.") in SHORTENERS),
        "has_port": int(port is not None),
        "has_punycode": int("xn--" in host),
        "double_slash_in_path": int("//" in path),
        "path_depth": len([p for p in path.split("/") if p]),
        "longest_token": max((len(t) for t in tokens), default=0),
        "entropy_url": round(entropy(low), 4),
        "entropy_host": round(entropy(host), 4),
        # bỏ tên miền chính trước khi đếm, tránh trường hợp "vietcombank" bị tính từ khóa "bank"
        "suspicious_keyword_count": sum(1 for k in SUSPICIOUS_KEYWORDS
                                        if k in (low.replace(reg, " ") if reg else low)),
        "brand_not_in_domain": brand_hit,
        "risky_tld": int((ext.suffix or "").split(".")[-1] in RISKY_TLDS),
        "free_hosting": int(any(h in host for h in FREE_HOSTING)),
        "has_file_ext": int(bool(re.search(r"\.(php|html?|aspx?|jsp|cgi|exe|apk|zip)$", path.lower()))),
        "has_www": int(host.startswith("www.")),
    }
    return f


def explain(url: str, f: dict | None = None) -> list[str]:
    """Liệt kê bằng chứng ký tự dễ hiểu để hiển thị cho người dùng (TV5 dùng)."""
    f = f or extract_features(url)
    _, _, host, _ = parse(url)
    r = []
    if f["has_ip_address"]:
        r.append("Tên miền là địa chỉ IP thay vì tên miền thông thường")
    if f["is_shortened"]:
        r.append("Dùng dịch vụ rút gọn link, không thấy được địa chỉ thật")
    if f["brand_not_in_domain"]:
        r.append("Có tên thương hiệu/tổ chức trong URL nhưng không phải tên miền chính thức")
    if f["suspicious_keyword_count"] >= 1:
        r.append(f"Chứa {f['suspicious_keyword_count']} từ khóa hay gặp trong trang giả mạo (login, verify, account...)")
    if f["risky_tld"]:
        r.append("Đuôi tên miền thuộc nhóm giá rẻ thường bị lạm dụng")
    if f["free_hosting"]:
        r.append("Trang đặt trên dịch vụ hosting/tạo web miễn phí")
    if f["subdomain_count"] >= 3:
        r.append(f"Có nhiều tên miền phụ ({f['subdomain_count']} cấp)")
    if f["host_hyphen_count"] >= 2:
        r.append("Tên miền có nhiều dấu gạch ngang")
    if f["host_digit_count"] >= 5:
        r.append("Tên miền chứa nhiều chữ số")
    if f["has_punycode"]:
        r.append("Tên miền dạng punycode (xn--), có thể giả ký tự giống chữ thật")
    if f["num_at"]:
        r.append("URL chứa ký tự @ (có thể che giấu địa chỉ thật)")
    if f["url_length"] > 100:
        r.append(f"URL dài bất thường ({f['url_length']} ký tự)")
    if f["entropy_host"] > 4.2:
        r.append("Tên miền có chuỗi ký tự lộn xộn (entropy cao)")
    if f["has_port"]:
        r.append("URL chỉ định cổng (port) riêng")
    return r
