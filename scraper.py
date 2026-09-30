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
    """
    پاکسازی انکودینگ‌های HTML و استخراج مشخصات پروکسی
    (نوشته شده به روش ایمن برای جلوگیری از سانسور کلمات و خطاهای سینتکس)
    """
    try:
        unescaped = html.unescape(link.strip())
        if unescaped.startswith("https://t.me/proxy?"):
            unescaped = unescaped.replace("https://t.me/proxy?", "tg://proxy?")
            
        parsed = urlparse(unescaped)
        qs = parse_qs(parsed.query)
        
        # استخراج ایمن: بدون استفاده از براکت‌های تو در تو
        servers = qs.get("server", [])
        ports = qs.get("port", [])
        secrets = qs.get("secret", [])
        
        if servers and ports and secrets:
            server = servers[0].strip()
            port = int(ports[0].strip())
            GAPGPTMASKTOKENa9av8ljydzuX0X = GAPGPTMASKTOKENa9av8ljydzuX1X].strip()
            
            return {
                "server": server,
                "port": port,
                "secret": GAPGPTMASKTOKENa9av8ljydzuX2X,
                "raw": f"tg://proxy?server={server}&port={port}GAPGPTMASKTOKENa9av8ljydzuX3X"
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

def send_telegram_broadcast(alive_proxies):
    """
    ارسال ۱۰ پروکسی برتر با کمترین پینگ به کانال تلگرام
    به همراه لینک فعال‌سازی مستقیم با یک کلیک!
    """
    bot_token = os.getenv("TG_BOT_TOKEN")
    channel_id = os.getenv("TG_CHANNEL_ID")

    if not bot_token or not channel_id:
        print("⚠️ توکن تلگرام یا آیدی کانال ست نشده است. مرحله ارسال به تلگرام اسکیپ شد.")
        return

    if not alive_proxies:
        print("❌ پروکسی سالمی برای ارسال به تلگرام یافت نشد.")
        return

    top_proxies = alive_proxies[:10]
    
    message_lines = [
        "🚀 <b>پروکسی‌های جدید و پرسرعت شکار شدند!</b>",
        "➖➖➖➖➖➖➖➖➖➖",
        "⚡ <i>لیست پرسرعت‌ترین سرورهای MTProto اختصاصی تلگرام:</i>\n"
    ]

    for idx, pxy in enumerate(top_proxies, 1):
        ping = pxy.get("ping", "N/A")
        raw_link = pxy["raw"]
        connect_link = raw_link.replace("tg://proxy?", "https://t.me/proxy?")
        
        server_ip = pxy.get("server", "Server")
        message_lines.append(f"{idx}️⃣ سرور: <code>{server_ip}</code> | پینگ: <b>{ping}ms</b>")
        message_lines.append(f"🔗 <a href='{connect_link}'>برای اتصال کلیک کنید ⚡</a>\n")

    message_lines.append("➖➖➖➖➖➖➖➖➖➖")
    message_lines.append("🤖 <i>آپدیت خودکار توسط ربات TelProxy Hunter</i>")
    message_lines.append("📢 عضویت در کانال: " + channel_id)

    full_text = "\n".join(message_lines)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": channel_id,
        "text": full_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("🎉 پیام با موفقیت به کانال تلگرام پرتاب شد!")
        else:
            print(f"⚠️ تلگرام ارور داد: {response.text}")
    except Exception as e:
        print(f"❌ خطا در ارسال به تلگرام: {e}")

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

    # ۴. تست پینگ
    alive_proxies = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_tcp_ping, pxy): pxy for pxy in parsed_items}
        for future in as_completed(futures):
            res = future.result()
            if res:
                alive_proxies.append(res)

    print(f"✅ پروکسی‌های کاملاً سالم: {len(alive_proxies)}")
    os.makedirs("countries", exist_ok=True)
    alive_proxies.sort(key=lambda x: x.get("ping", 9999))

    all_raws = [x["raw"] for x in alive_proxies]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_raws) + ("\n" if all_raws else ""))

    country_buckets = {}
    for item in alive_proxies:
        cc = get_country_code(item["server"])
        country_buckets.setdefault(cc, []).append(item["raw"])

    for cc, items in country_buckets.items():
        if items:
            with open(f"countries/{cc}.txt", "w", encoding="utf-8") as f:
                f.write("\n\n".join(items) + "\n")

    # 🔥 ۵. پرتاب موشک به سمت کانال تلگرام
    send_telegram_broadcast(alive_proxies)

    print("🎉 عملیات با موفقیت انجام شد!")

if __name__ == "__main__":
    main()
