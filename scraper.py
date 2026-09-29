"""
=============================================================================
*  Project: Telegram MTProto Proxy Hunter (Bulletproof Edition) 🚀
*  Author: mm.keshavarz | TelProxy
=============================================================================
"""

import os
import re
import socket
import requests
import html
import time
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

# 💎 ۱. کانال‌های فعال تلگرام (نسخه وب)
CHANNELS = [
    "ProxyMTProto", "TelMTProto", "Proxy_MTProto", 
    "MTProtoProxies", "proxyme", "PinkProxy", 
    "ProxyDaemi", "MTP_roxy", "Tel_Proxies", "iProxyMTProto"
]

# 🌐 ۲. سورس‌های خام کمکی (اگه تلگرام وب ناز کرد، اینا جور بقیه رو می‌کشن!)
BACKUP_SOURCES = [
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.json",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# ریجکس دقیق برای گرفتن پروکسی تلگرام
REGEX_PATTERN = r'(tg://proxy\?[^\s<"\'\n]+|https://t\.me/proxy\?[^\s<"\'\n]+)'

MAX_TIMEOUT = 3.5  # دست‌ودلبازتر برای سرورهای گیت‌هاب خارج از کشور
MAX_WORKERS = 35

def clean_and_parse(link: str):
    """پاکسازی انکودینگ‌های HTML و پارس امن سرور و پورت"""
    try:
        # حل باگ تاریخی: تبدیل &amp; به & واقعی
        unescaped = html.unescape(link.strip())
        
        if unescaped.startswith("https://t.me/proxy?"):
            unescaped = unescaped.replace("https://t.me/proxy?", "tg://proxy?")
            
        parsed = urlparse(unescaped)
        qs = parse_qs(parsed.query)
        
        server = qs.get("server", [None])[0]
        port = qs.get("port", [None])[0]
        secret = qs.get("secret", [None])[0]
        
        if server and port and secret:
            return {
                "server": server.strip(),
                "port": int(port.strip()),
                "secret": secret.strip(),
                "raw": f"tg://proxy?server={server.strip()}&port={port.strip()}&secret={secret.strip()}"
            }
    except Exception:
        pass
    return None

def check_tcp_ping(proxy_data):
    """تست باز بودن پورت و تاخیر ارتباطی"""
    if not proxy_data:
        return None
    
    server = proxy_data["server"]
    port = proxy_data["port"]

    if server in ["127.0.0.1", "localhost", "0.0.0.0"]:
        return None

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(MAX_TIMEOUT)
    
    start_time = time.time()
    try:
        sock.connect((server, port))
        latency = round((time.time() - start_time) * 1000, 2)
        sock.close()
        proxy_data["ping"] = latency
        return proxy_data
    except Exception:
        sock.close()
        return None

GEO_CACHE = {}

def get_country_code(server: str) -> str:
    """شناسایی لوکیشن سرور با کش"""
    if server in GEO_CACHE:
        return GEO_)
        
        server = qs.get("server", [None])[0]
        port = qs.get("port", [None])[0]
        secret = qs.get("secret", [None])[0]
        
        if server and port and secret:
            return {
                "server": server.strip(),
                "port": int(port.strip()),
                "secret": secret.strip(),
                "raw": f"tg://proxy?server={server.strip()}&port={port.strip()}&secret={secret.strip()}"
            }
    except Exception:
        pass
    return None

def check_tcp_ping(proxy_data):
    """تست باز بودن پورت و تاخیر ارتباطی"""
    if not proxy_data:
        return None
    
    server = proxy_data["server"]
    port = proxy_data["port"]

    if server in ["127.0.0.1", "localhost", "0.0.0.0"]:
        return None

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(MAX_TIMEOUT)
    
    start_time = time.time()
    try:
        sock.connect((server, port))
        latency = round((time.time() - start_time) * 1000, 2)
        sock.close()
        proxy_data["ping"] = latency
        return proxy_data
    except Exception:
        sock.close()
        return None

GEO_CACHE = {}

def get_country_code(server: str) -> str:
    """شناسایی لوکیشن سرور با کش"""
    if server in GEO_CACHE:
        return GEO_CACHE[server]
    
    try:
        ip_addr = socket.gethostbyname(server)
        res = requests.get(f"http://ip-api.com/json/{ip_addr}?fields=countryCode,status", timeout=2.5)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                country
            pass

    # پاکسازی اولیه و پارس
    unique_links = list(set(raw_candidates))
    parsed_items = []
    for link in unique_links:
        item = clean_and_parse(link)
        if item:
            parsed_items.append(item)

    print(f"\n📦 مجموع پروکسی‌های معتبر پارس شده: {len(parsed_items)}")

    # گام سوم: تست زنده بودن (TCP Ping)
    print("⚡ در حال تست پینگ و بررسی سلامت پورت‌ها...")
    alive_proxies = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_tcp_ping, pxy): pxy for pxy in parsed_items}
        for future in as_completed(futures):
            res = future.result()
            if res:
                alive_proxies.append(res)

    print(f"✅ پروکسی‌های کاملاً سالم و آنلاین: {len(alive_proxies)}")

    # تضمین ساخت فولدر کشورها
    os.makedirs("countries", exist_ok=True)

    if not alive_proxies:
        print("⚠️ هیچ سروری پاسخ نداد! برای حفظ ساختار، یک نمونه تست ذخیره می‌شود.")
        # جلوگیری از خالی موندن مطلق فایل در شرایط اضطراری
        alive_proxies.append({
            "raw": "tg://proxy?server=127.0.0.1&port=443&secret=ee000000000000000000000000000000007777772e636c6f7564666c6172652e636f6d",
            "ping": 999,
            "server": "127.0.0.1"
        })

    # مرتب‌سازی بر اساس کمترین پینگ
    alive_proxies.sort(key=lambda x: x.get("ping", 9999))

    # ذخیره در فایل اصلی sub.txt
    all_raws = [x["raw"] for x in alive_proxies]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_raws) + "\n")

    # دسته‌بندی کشوری
    country_buckets = {}
    for item in alive_proxies:
        cc = get_country_code(item["server"])
        if cc not in country_buckets:
            country_buckets[cc] = []
        country_buckets[cc].append(item["raw"])

    for cc, items in country_buckets.items():
        if items:
            with open(f"countries/{cc}.txt", "w", encoding="utf-8") as f:
                f.write("\n\n".join(items) + "\n")

    print("🎉 کار تمومه! فایل sub.txt و فولدر countries با موفقیت به‌روزرسانی شدند.")

if __name__ == "__main__":
    main()
