#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru через API Selectel (пробуем разные варианты)"""
import urllib.request, json, time, socket

PROJECT_ID = "635e27ae-0b55-44ff-abc8-bf557c43076b"
API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"
DOMAIN = "beklox.ru"
IP = "139.100.234.22"

# Пробуем разные способы аутентификации
print("=== Пробуем разные способы аутентификации ===")

# Способ 1: X-Token (старый API)
print("\n1. X-Token...")
try:
    url = "https://api.selectel.ru/domains/v1/zones"
    headers = {"X-Token": API_KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"  ✅ {resp.read().decode()[:200]}")
except urllib.error.HTTPError as e:
    print(f"  ❌ {e.code}: {e.read().decode()[:200]}")

# Способ 2: X-Domain-Token
print("\n2. X-Domain-Token...")
try:
    url = "https://api.selectel.ru/domains/v1/zones"
    headers = {"X-Domain-Token": API_KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"  ✅ {resp.read().decode()[:200]}")
except urllib.error.HTTPError as e:
    print(f"  ❌ {e.code}: {e.read().decode()[:200]}")

# Способ 3: X-Auth-Token через OpenStack (с правильным user.name вместо user.id)
print("\n3. OpenStack с user.name...")
auth_data = json.dumps({
    "auth": {
        "identity": {
            "methods": ["password"],
            "password": {
                "user": {
                    "name": PROJECT_ID,
                    "password": API_KEY,
                    "domain": {"name": "users"}
                }
            }
        },
        "scope": {
            "project": {
                "id": PROJECT_ID
            }
        }
    }
}).encode()

try:
    url = "https://api.selectel.ru/identity/v3/auth/tokens"
    req = urllib.request.Request(url, data=auth_data, headers={"Content-Type": "application/json"}, method="POST")
    resp = urllib.request.urlopen(req, timeout=30)
    token = resp.headers.get("X-Subject-Token")
    print(f"  ✅ Токен: {token[:50] if token else 'None'}...")
    
    if token:
        # Пробуем DNS API
        for ep in [
            "https://api.selectel.ru/dns/v2/zones",
            "https://api.selectel.ru/dns/v1/zones",
            "https://api.selectel.ru/domains/v1/zones",
        ]:
            try:
                req2 = urllib.request.Request(ep, headers={"X-Auth-Token": token})
                resp2 = urllib.request.urlopen(req2, timeout=30)
                body = resp2.read()
                print(f"  ✅ {ep}: {body.decode()[:200]}")
            except urllib.error.HTTPError as e2:
                print(f"  ❌ {ep}: {e2.code}")
except urllib.error.HTTPError as e:
    print(f"  ❌ {e.code}: {e.read().decode()[:200]}")
except Exception as e:
    print(f"  ❌ {e}")

# Способ 4: API ключ как Bearer token
print("\n4. Bearer token...")
try:
    url = "https://api.selectel.ru/domains/v1/zones"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"  ✅ {resp.read().decode()[:200]}")
except urllib.error.HTTPError as e:
    print(f"  ❌ {e.code}: {e.read().decode()[:200]}")

# Способ 5: Пробуем через панель управления (my.selectel.ru API)
print("\n5. API панели управления...")
try:
    url = "https://my.selectel.ru/api/v1/domains"
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"  ✅ {resp.read().decode()[:200]}")
except urllib.error.HTTPError as e:
    print(f"  ❌ {e.code}: {e.read().decode()[:200]}")

print("\n=== Проверка DNS ===")
try:
    ip = socket.gethostbyname(DOMAIN)
    print(f"  {DOMAIN} -> {ip}")
except:
    print(f"  {DOMAIN} -> NXDOMAIN")
