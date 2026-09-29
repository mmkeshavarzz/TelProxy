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

# 💎 ۱. کانال‌های تلگرام برای استخراج پروکسی
CHANNELS = [
    "ProxyMTProto", "TelMTProto", "Proxy_MTProto", 
    "MTProtoProxies", "proxyme", "PinkProxy", 
    "ProxyDaemi", "MTP_roxy", "Tel_Proxies", "iProxyMTProto"
]

# 🌐 ۲. سورس‌های خام کمکی
BACKUP_SOURCES = [
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.json",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

REGEX_PATTERN = r'(tg://proxy\?[^\s<"\'\n]+|https://t\.me/proxy\?[^\s<"\'\n]+)'
MAX_TIMEOUT = 3.5
MAX_WORKERS = 35
GEO_CACHE = {}

def clean_and_parse(link: str):
    """پاکسازی انکودینگ‌های HTML و استخراج مشخصات پروکسی"""
    try:
        unescaped = html.unescape(link.strip())
        if unescaped.startswith("https://t.me/proxy?"):
            unescaped = unescaped.replace("https://t.me/proxy?", "tg://proxy?")
            
        parsed = urlparse(unescaped)
        qs = parse_qs(parsed.query)
        
        server = GAPGPTMASKTOKENskewhljzbsX0X"server", [None])[0]
        port = GAPGPTMASKTOKENskewhljzbsX1X"port", [None])[0]
        secret = GAPGPTMASKTOKENskewhljzbsX2X"secret", [None])[0]
        
        if server and port and secret:
            server = server.strip()
            port = int(port.strip())
            secret = GAPGPTMASKTOKENskewhljzbsX3X
            return {
                "server": server,
                "port": port,
                "secret": secret,
                "raw": f"tg://proxy?server={server}&port={port}GAPGPTMASKTOKENskewhljzbsX4X"
            }
    except Exception:
        pass
    return None

def check_tcp_ping(proxy_data):
    """تست باز بودن پورت و اندازه‌گیری پینگ"""
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

def get_country_code(server: str) -> str:
    """شناسایی لوکیشن سرور با کش برای جلوگیری از بلاک شدن"""
    if server in GEO_CACHE:
        return GEO_CACHE[server]
    
    try:
        ip_addr = socket.gethostbyname(server)
        res = requests.get(f"http://ip-api.com/json/{ip_addr}?fields=countryCode,status", timeout=2.5)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                cc = data.get("countryCode", "OTHER")
                GEO_CACHE[server] = cc
                return cc
    except Exception:
        pass
    
    GEO_CACHE[server] = "OTHER"
    return "OTHER"

def main():
    print("🚀 استارت موتور جمع‌آوری پروکسی تلگرام...")
    raw_candidates = []

    # ۱. واکشی از کانال‌های تلگرام وب
    for ch in CHANNELS:
        url = f"https://t.me/s/{ch}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                matches = re.findall(REGEX_PATTERN, r.text)
                print(f"📡 کانال @{ch}: {len(matches)} لینک خام یافت شد.")
                raw_candidates.extend(matches)
        except Exception as e:
            print(f"⚠️ کانال @{ch} با خطا مواجه شد: {e}")

    # ۲. واکشی از سورس‌های پشتیبان
    for src in BACKUP_SOURCES:
        try:
            r = requests.get(src, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                matches = re.findall(REGEX_PATTERN, r.text)
                name = src.split("/")[-1]
                print(f"🌐 سورس پشتیبان {name}: {len(matches)} لینک یافت شد.")
                raw_candidates.extend(matches)
        except Exception:
            pass

    # ۳. حذف لینک‌های تکراری و پارس کردن
    unique_links = list(set(raw_candidates))
    parsed_items = []
    for link in unique_links:
        item = clean_and_parse(link)
        if item:
            parsed_items.append(item)

    print(f"\n📦 مجموع پروکسی‌های معتبر پارس شده: {len(parsed_items)}")

    # ۴. تست پینگ و زنده بودن سرورها
    print("⚡ در حال تست پینگ و بررسی سلامت پورت‌ها...")
    alive_proxies = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_tcp_ping, pxy): pxy for pxy in parsed_items}
        for future in as_completed(futures):
            res = future.result()
            if res:
                alive_proxies.append(res)

    print(f"✅ پروکسی‌های کاملاً سالم و آنلاین: {len(alive_proxies)}")

    # ایجاد پوشه countries در صورت عدم وجود
    os.makedirs("countries", exist_ok=True)

    # مرتب‌سازی بر اساس کمترین تاخیر (Fastest First)
    alive_proxies.sort(key=lambda x: x.get("ping", 9999))

    # ۵. ذخیره فایل اصلی sub.txt
    all_raws = [x["raw"] for x in alive_proxies]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_raws) + ("\n" if all_raws else ""))

    # ۶. دسته‌بندی کشوری و ذخیره در پوشه countries
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

    print("🎉 عملیات با موفقیت انجام شد! فایل sub.txt و فولدر countries آپدیت شدند.")

if __name__ == "__main__":
    main()
