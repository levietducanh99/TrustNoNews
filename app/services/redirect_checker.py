# services/redirect_checker.py
import requests
from urllib.parse import urlparse, parse_qs, unquote, urljoin
from url_normalize import url_normalize
import re
import os
import html
import time
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_text_file_to_list(file_path):
    """Đọc file văn bản và trả về danh sách các dòng không rỗng."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        logger.warning(f"Không thể đọc file {file_path}: {e}")
        return []

def get_data_directory():
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        current_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
    return os.path.join(current_dir, 'data')

def initialize_keywords_and_domains():
    data_dir = get_data_directory()
    suspicious_keywords_path = os.path.join(data_dir, 'suspicious_keywords.txt')
    dangerous_domains_path = os.path.join(data_dir, 'dangerous_domains.txt')

    suspicious_keywords = load_text_file_to_list(suspicious_keywords_path)
    if not suspicious_keywords:
        logger.warning("Sử dụng danh sách từ khóa mặc định.")
        suspicious_keywords = ["shop", "store", "click", "ad", "redirect", "affiliate",
                               "product", "promo", "offer", "deal", "sale", "buy"]

    dangerous_domains = [d.lower().lstrip("www.") for d in load_text_file_to_list(dangerous_domains_path)]
    return suspicious_keywords, dangerous_domains

SUSPICIOUS_KEYWORDS, DANGEROUS_DOMAINS = initialize_keywords_and_domains()

def normalize_url(url):
    if not url:
        return ""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    try:
        return url_normalize(url)
    except Exception as e:
        logger.warning(f"Lỗi khi chuẩn hóa URL: {e}")
        return url

def extract_embedded_url(url):
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    redirect_mappings = {
        ('facebook.com', 'fb.com'): ['u', 'next', 'ref'],
        ('google.com'): ['url', 'q', 'u', 'continue'],
        ('youtube.com'): ['q', 'url', 'next'],
        ('twitter.com', 'x.com'): ['url', 'redirect_to'],
        ('linkedin.com'): ['url', 'redirect'],
        ('instagram.com'): ['url', 'next'],
        ('t.co'): ['url'],
        ('bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly'): ['target']
    }

    for domains, params in redirect_mappings.items():
        domains_list = domains if isinstance(domains, tuple) else (domains,)
        if any(domain in parsed.netloc.lower() for domain in domains_list):
            for param in params:
                if param in query_params:
                    return unquote(query_params[param][0])

    redirect_params = ['url', 'link', 'target', 'dest', 'destination', 'redirect',
                       'redirecturl', 'to', 'goto', 'return', 'returnto', 'location', 'href']
    for param in redirect_params:
        if param in query_params:
            return unquote(query_params[param][0])
    return url

def is_suspicious_url(url):
    url_lower = url.lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.lower() in url_lower:
            return True, f"URL chứa từ khóa đáng ngờ: {keyword}"

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    for key, values in query_params.items():
        key_lower = key.lower()
        for value in values:
            value_lower = value.lower()
            for keyword in SUSPICIOUS_KEYWORDS:
                keyword_lower = keyword.lower()
                if keyword_lower in value_lower or keyword_lower in key_lower:
                    return True, f"Tham số URL chứa từ khóa đáng ngờ: {keyword}"

    if len(query_params) > 10:
        return True, f"URL có quá nhiều tham số query ({len(query_params)})"
    return False, ""

def is_dangerous_domain(url):
    if not url:
        return False, ""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower().lstrip("www.")
    if domain in DANGEROUS_DOMAINS:
        return True, f"Domain {domain} nằm trong danh sách nguy hiểm"
    parts = domain.split('.')
    for i in range(1, len(parts)):
        parent_domain = '.'.join(parts[i:])
        if parent_domain in DANGEROUS_DOMAINS:
            return True, f"Domain {parent_domain} nằm trong danh sách nguy hiểm"
    return False, ""

def extract_url_from_html(html_content, base_url):
    extracted_urls = []
    patterns = {
        'meta_refresh': r'<meta[^>]*?http-equiv=["\']?refresh["\']?[^>]*?content=["\']?\d+;\s*url=(.*?)["\'\s>]',
        'canonical': r'<link[^>]*?rel=["\']?canonical["\']?[^>]*?href=["\']?([^"\'>]+)["\']?'
    }
    js_patterns = [
        r'window\.location(?:\.href)?\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'location\.replace\([\'"]([^\'"]+)[\'"]\)',
        r'location\.assign\([\'"]([^\'"]+)[\'"]\)',
        r'location\.href\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'document\.location\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'self\.location\s*=\s*[\'"]([^\'"]+)[\'"]',
        r'top\.location\s*=\s*[\'"]([^\'"]+)[\'"]'
    ]

    for redirect_type, pattern in patterns.items():
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            url = html.unescape(match.group(1).strip())
            extracted_urls.append((redirect_type, urljoin(base_url, url)))

    for pattern in js_patterns:
        match = re.search(pattern, html_content)
        if match:
            url = html.unescape(match.group(1).strip())
            extracted_urls.append(('javascript', urljoin(base_url, url)))
    return extracted_urls

def deduplicate_warnings(warnings):
    """Removes duplicate warning messages."""
    if not warnings:
        return []
    
    unique_warnings = []
    seen = set()
    
    for warning in warnings:
        # Create a simplified version for deduplication
        simple_warning = re.sub(r'(URL|ĐÁNG NGỜ|NGUY HIỂM):', '', warning).strip()
        simple_warning = re.sub(r'\bshop\b', 'shop_keyword', simple_warning)
        
        if simple_warning not in seen:
            seen.add(simple_warning)
            unique_warnings.append(warning)
            
    return unique_warnings

def check_redirect_and_validate(url, timeout=10, max_redirects=5):
    redirect_chain = []
    warning_messages = []

    embedded_url = extract_embedded_url(url)
    if embedded_url != url:
        url = embedded_url
        redirect_chain.append({'step': 1, 'type': 'embedded', 'url': url})
        warning_messages.append(f"URL chứa liên kết nhúng: {url}")

    url = normalize_url(url)
    if not url:
        return None, "URL không hợp lệ", redirect_chain

    is_dangerous, dangerous_reason = is_dangerous_domain(url)
    if is_dangerous:
        return None, f"NGUY HIỂM: {dangerous_reason}", redirect_chain

    is_suspicious, suspicious_reason = is_suspicious_url(url)
    if is_suspicious:
        warning_messages.append(f"ĐÁNG NGỜ: {suspicious_reason}")

    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        }

        current_url = url
        redirect_count = 0
        step_count = len(redirect_chain) + 1

        while redirect_count < max_redirects:
            try:
                logger.info(f"Đang truy cập: {current_url}")
                response = session.get(current_url, timeout=timeout, allow_redirects=False, headers=headers)

                if response.status_code in (301, 302, 303, 307, 308):
                    if 'Location' in response.headers:
                        next_url = urljoin(current_url, response.headers['Location'])
                        redirect_chain.append({
                            'step': step_count,
                            'type': 'http',
                            'url': next_url
                        })
                        step_count += 1

                        is_dangerous, dangerous_reason = is_dangerous_domain(next_url)
                        if is_dangerous:
                            return None, f"NGUY HIỂM: Redirect tới {dangerous_reason}", redirect_chain

                        is_suspicious, suspicious_reason = is_suspicious_url(next_url)
                        if is_suspicious:
                            warning_messages.append(f"ĐÁNG NGỜ: Redirect {suspicious_reason}")

                        current_url = next_url
                        redirect_count += 1
                        time.sleep(0.5)
                        continue
                    else:
                        warning_messages.append("Phát hiện chuyển hướng nhưng không có header Location")
                        break

                final_url = current_url
                try:
                    final_html = response.text
                    html_redirects = extract_url_from_html(final_html, final_url)
                    for redirect_type, redirect_url in html_redirects:
                        if redirect_url != final_url:
                            redirect_chain.append({
                                'step': step_count,
                                'type': redirect_type,
                                'url': redirect_url
                            })
                            step_count += 1

                            is_dangerous, dangerous_reason = is_dangerous_domain(redirect_url)
                            if is_dangerous:
                                return None, f"NGUY HIỂM: {redirect_type} redirect tới {dangerous_reason}", redirect_chain

                            is_suspicious, suspicious_reason = is_suspicious_url(redirect_url)
                            if is_suspicious:
                                warning_messages.append(f"ĐÁNG NGỜ: {redirect_type} redirect {suspicious_reason}")

                            if redirect_type in ['meta_refresh', 'canonical']:
                                final_url = redirect_url
                except Exception as e:
                    warning_messages.append(f"Không thể phân tích nội dung HTML: {e}")

                break
            except requests.RequestException as e:
                return None, f"Lỗi khi truy cập {current_url}: {e}", redirect_chain
            except Exception as e:
                return None, f"Lỗi không xác định: {e}", redirect_chain

        if redirect_count >= max_redirects:
            warning_messages.append(f"Quá nhiều chuyển hướng (>{max_redirects})")

        if warning_messages:
            # Deduplicate warning messages before joining
            unique_warnings = deduplicate_warnings(warning_messages)
            return final_url, " | ".join(unique_warnings), redirect_chain

        return final_url, None, redirect_chain

    except Exception as e:
        return None, f"Lỗi khi kiểm tra redirect: {e}", redirect_chain
