#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru через API Selectel (v2)"""
import urllib.request, json, time, socket

PROJECT_ID = "635e27ae-0b55-44ff-abc8-bf557c43076b"
API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"
DOMAIN = "beklox.ru"
IP = "139.100.234.22"

def api_call(method, path, data=None, use_token=True):
    url = f"https://api.selectel.ru/domains/v1/{path}"
    
    if use_token:
        # Пробуем с X-Token
        headers = {
            "X-Token": API_KEY,
            "Content-Type": "application/json"
        }
    else:
        headers = {
            "X-Domain-Token": API_KEY,
            "Content-Type": "application/json"
        }
    
    if data:
        data = data.encode() if isinstance(data, str) else data
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ❌ {method} {path}: {e.code}")
        if e.code == 401:
            return "UNAUTHORIZED"
        return None
    except Exception as e:
        print(f"  ❌ {method} {path}: {e}")
        return None

# Пробуем разные варианты аутентификации
print("=== Пробуем разные варианты API ===")

# Вариант 1: X-Token
print("\n1. Пробуем X-Token...")
result = api_call("GET", "zones", use_token=True)
if result and result != "UNAUTHORIZED":
    print(f"  ✅ X-Token работает! Зоны: {result}")
elif result == "UNAUTHORIZED":
    print("  ❌ X-Token не подошёл")
    
    # Вариант 2: X-Domain-Token
    print("\n2. Пробуем X-Domain-Token...")
    result = api_call("GET", "zones", use_token=False)
    if result and result != "UNAUTHORIZED":
        print(f"  ✅ X-Domain-Token работает! Зоны: {result}")
    elif result == "UNAUTHORIZED":
        print("  ❌ X-Domain-Token тоже не подошёл")

# Вариант 3: другой эндпоинт
print("\n3. Пробуем другой эндпоинт (dns.api.selectel.ru)...")
try:
    url = "https://dns.api.selectel.ru/v1/zones"
    headers = {"X-Token": API_KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"  ✅ Ответ: {resp.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"  ❌ {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"  ❌ {e}")

# Вариант 4: API Selectel Cloud
print("\n4. Пробуем API Selectel Cloud (api.selectel.ru)...")
try:
    url = "https://api.selectel.ru/v1/projects"
    headers = {"X-Auth-Token": API_KEY, "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=30)
    print(f"  ✅ Ответ: {resp.read().decode()[:200]}")
except urllib.error.HTTPError as e:
    print(f"  ❌ {e.code}: {e.read().decode()[:200]}")
except Exception as e:
    print(f"  ❌ {e}")

# Вариант 5: OpenStack API (если это OpenStack проект)
print("\n5. Пробуем получить токен OpenStack...")
try:
    url = "https://api.selectel.ru/identity/v3/auth/tokens"
    data = json.dumps({
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": PROJECT_ID,
                        "password": API_KEY,
                        "domain": {"id": "default"}
                    }
                }
            }
        }
    }).encode()
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    resp = urllib.request.urlopen(req, timeout=30)
    token = resp.headers.get("X-Subject-Token")
    print(f"  ✅ Токен получен: {token[:50]}...")
    
    # Пробуем создать DNS зону с этим токеном
    url2 = "https://api.selectel.ru/dns/v2/zones"
    data2 = json.dumps({"name": DOMAIN, "email": "dlyavsego02@mail.ru"}).encode()
    headers2 = {"X-Auth-Token": token, "Content-Type": "application/json"}
    req2 = urllib.request.Request(url2, data=data2, headers=headers2, method="POST")
    try:
        resp2 = urllib.request.urlopen(req2, timeout=30)
        print(f"  ✅ DNS зона создана: {resp2.read().decode()}")
    except urllib.error.HTTPError as e2:
        print(f"  ❌ {e2.code}: {e2.read().decode()[:200]}")
except urllib.error.HTTPError as e:
    print(f"  ❌ {e.code}: {e.read().decode()[:200]}")
except Exception as e:
    print(f"  ❌ {e}")

print("\n=== Проверка DNS ===")
try:
    ip = socket.gethostbyname(DOMAIN)
    print(f"  {DOMAIN} -> {ip}")
except:
    print(f"  {DOMAIN} -> NXDOMAIN")
