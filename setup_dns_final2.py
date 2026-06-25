#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru - исследуем API Selectel"""
import urllib.request, json, time, socket

API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"
DOMAIN = "beklox.ru"
IP = "139.100.234.22"

def try_api(method, url, data=None, headers_extra=None):
    headers = {"X-Token": API_KEY, "Content-Type": "application/json"}
    if headers_extra:
        headers.update(headers_extra)
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]
    except Exception as e:
        return 0, str(e)

# Исследуем разные эндпоинты
endpoints = [
    # DNS API
    ("GET", "https://api.selectel.ru/domains/v1/zones"),
    ("GET", "https://api.selectel.ru/domains/v1/zones/"),
    ("GET", "https://api.selectel.ru/domains/v1/domains"),
    ("GET", "https://api.selectel.ru/domains/v1/domains/"),
    ("POST", "https://api.selectel.ru/domains/v1/domains", {"name": DOMAIN}),
    ("POST", "https://api.selectel.ru/domains/v1/zones", {"name": DOMAIN, "email": "dlyavsego02@mail.ru"}),
    # Альтернативные пути
    ("GET", "https://api.selectel.ru/v1/domains"),
    ("GET", "https://api.selectel.ru/v2/domains"),
    ("GET", "https://api.selectel.ru/domains"),
    ("GET", "https://api.selectel.ru/dns"),
    ("GET", "https://api.selectel.ru/dns/zones"),
    # API панели управления
    ("GET", "https://my.selectel.ru/api/v1/domains"),
    ("GET", "https://my.selectel.ru/api/domains"),
]

print("=== Исследуем API Selectel ===\n")
for method, url, *data in endpoints:
    d = data[0] if data else None
    status, result = try_api(method, url, d)
    status_str = f"✅ {status}" if status == 200 else f"❌ {status}"
    result_str = str(result)[:100] if isinstance(result, str) else json.dumps(result)[:100]
    print(f"{status_str} {method} {url}")
    if status == 200:
        print(f"   Ответ: {result_str}")
    print()
