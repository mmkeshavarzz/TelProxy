"""
=============================================================================
*  Project: Telegram Proxy Hunter & Auto Categorizer (Turbine Style) 🚀
*  Author: mm.keshavarz | Modified for MTProto Proxies
*  Features:
*    - Multi-threaded TCP Ping & Handshake latency tester
*    - MTProto parser (tg://proxy & https://t.me/proxy)
*    - GeoIP lookup (Countries: DE, US, TR, NL, etc.)
*    - Clean folder structuring (Raw Text Format for Telegram)
=============================================================================
"""

import os
import re
import socket
import requests
import time
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

# 💎 ۱. کانال‌های هدف (مخصوص پروکسی تلگرام)
CHANNELS = [
    "ProxyMTProto", "TelMTProto", "Proxy_MTProto", 
    "MTProtoProxies", "proxyme", "PinkProxy", 
    "ProxyDaemi", "MTP_roxy", "Tel_Proxies"
    # هرچی کانال خوب پروکسی می‌شناسی اینجا بریز!
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# پیدا کردن لینک‌های tg://proxy و https://t.me/proxy
REGEX_PATTERN = r'(tg://proxy\?[^\s<"\'\n]+|https://t\.me/proxy\?[^\s<"\'\n]+)'

# سقف تاخیر مجاز کانکشن به ثانیه (پروکسی تلگرام باید سریع باشه!)
MAX_TIMEOUT = 2.0
MAX_WORKERS = 40  # سرعت بالا با تردینگ

# =============================================================================
#  بخش اول: پارس و استخراج اطلاعات اتصال (IP / Port / Secret)
# =============================================================================

def parse_proxy(proxy_str: str):
    """تبدیل و استخراج سرور و پورت از لینک پروکسی تلگرام"""
    try:
        # استانداردسازی همه لینک‌ها به tg://
        if proxy_str.startswith("https://t.me/proxy?"):
            proxy_str = proxy_str.replace("https://t.me/proxy?", "tg://proxy?")
            
        parsed = urlparse(proxy_str)
        qs = parse_qs(parsed.query)
        
        server = qs.get("server", [None])[0]
        port = qs.get("port", [None])[0]
        
        if server and port:
            return {
                "server": server,
                "port": int(port),
                "raw": proxy_str
            }
    except Exception:
        pass
    return None

# =============================================================================
#  بخش دوم: تست حیات، پینگ و صحت پورت سرور (TCP Ping)
# =============================================================================

def check_alive_and_ping(proxy_data):
    """
    تست برقراری ارتباط با پورت باز سرور
    پروکسی‌های مرده همینجا خاکسپاری میشن! 🪦
    """
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
        # در زدن به سرور (تست اتصال مستقیم سوکت)
        sock.connect((server, port))
        latency = round((time.time() - start_time) * 1000, 2)
        sock.close()
        
        proxy_data["ping"] = latency
        return proxy_data
    except Exception:
        # یا پورت بسته‌ست یا سرور رفته گل بچینه
        sock.close()
        return None

# =============================================================================
#  بخش سوم: دریافت موقعیت جغرافیایی سرور (GeoIP)
# =============================================================================

GEO_CACHE = {}

def get_country_code(server: str) -> str:
    """تشخیص کشور بر اساس IP سرور به صورت کش‌شده"""
    if server in GEO_CACHE:
        return GEO_CACHE[server]
    
    try:
        ip_addr = socket.gethostbyname(server)
        res = requests.get(f"http://ip-api.com/json/{ip_addr}?fields=countryCode,status", timeout=2)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                country = data.get("countryCode", "OTHER").upper()
                GEO_CACHE[server] = country
                return country
    except Exception:
        pass
    
    GEO_CACHE[server] = "OTHER"
    return "OTHER"

# =============================================================================
#  موتور اصلی اسکرپ و فرآیند تولید خروجی
# =============================================================================

def main():
    print("🕵️‍♂️ در حال نفوذ به کانال‌های تلگرامی برای استخراج پروکسی...")
    raw_proxies = []

    for ch in CHANNELS:
        try:
            url = f"https://t.me/s/{ch}"
            res = requests.get(url, headers=HEADERS, timeout=12)
            if res.status_code == 200:
                found = re.findall(REGEX_PATTERN, res.text)
                cleaned = [c.strip() for c in found]
                print(f"📡 کانال {ch}: استخراج {len(cleaned)} پروکسی.")
                raw_proxies.extend(cleaned)
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ کانال {ch} در دسترس نبود (شاید فیلتره!).")

    unique_raw = list(set(raw_proxies))
    print(f"\n📦 مجموع پروکسی‌های خام و یونیک: {len(unique_raw)}")

    print("\n⚡ در حال پارس و تست پینگ همزمان (فیلتر پروکسی‌های زنده)...")
    parsed_items = [parse_proxy(c) for c in unique_raw if parse_proxy(c)]
    
    alive_proxies = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_pxy = {executor.submit(check_alive_and_ping, pxy): pxy for pxy in parsed_items}
        for future in as_completed(future_to_pxy):
            result = future.result()
            if result:
                alive_proxies.append(result)

    print(f"✨ پروکسی‌های تست شده و کاملاً زنده: {len(alive_proxies)}")

    if not alive_proxies:
        print("❌ هیچ پروکسی فعالی یافت نشد! تلگرام امروز خیلی سخت‌گیر شده...")
        return

    # مرتب‌سازی بر اساس کمترین پینگ (سریع‌ترین‌ها اول لیست باشن)
    alive_proxies.sort(key=lambda x: x.get("ping", 9999))

    # ایجاد پوشه‌ برای کشورها (پروتکل حذف شد چون همه MTProto هستن)
    os.makedirs("countries", exist_ok=True)
    country_buckets = {}

    print("🌍 در حال تعیین موقعیت جغرافیایی و دسته‌بندی نهایی...")
    for item in alive_proxies:
        cc = get_country_code(item["server"])
        if cc not in country_buckets:
            country_buckets[cc] = []
        country_buckets[cc].append(item["raw"])

    # ذخیره فایل‌های کشورها (به صورت خام، چون تلگرام Base64 نمی‌خواد)
    for cc, items in country_buckets.items():
        if items:
            raw_text = "\n\n".join(items) # با دوتا اینتر فاصله می‌دیم که تو تلگرام راحت کپی بشه
            with open(f"countries/{cc}.txt", "w", encoding="utf-8") as f:
                f.write(raw_text)

    # ذخیره ساب اصلی sub.txt (گلچین بهترین‌ها)
    all_alive_raw = [x["raw"] for x in alive_proxies]
    final_raw = "\n\n".join(all_alive_raw)

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_raw)

    print("🎉 عملیات Proxy Hunter با موفقیت به پایان رسید!")
    print(f"🌐 پراکندگی کشورها: { {k: len(v) for k, v in country_buckets.items()} }")

if __name__ == "__main__":
    main()
