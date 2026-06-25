#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru через API Selectel (правильная аутентификация)"""
import urllib.request, json, time, socket

PROJECT_ID = "635e27ae-0b55-44ff-abc8-bf557c43076b"
API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"
DOMAIN = "beklox.ru"
IP = "139.100.234.22"

# Шаг 1: Получаем токен через OpenStack Keystone
print("=== Шаг 1: Получаем токен аутентификации ===")

auth_data = json.dumps({
    "auth": {
        "identity": {
            "methods": ["password"],
            "password": {
                "user": {
                    "id": PROJECT_ID,
                    "password": API_KEY
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
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=auth_data, headers=headers, method="POST")
    resp = urllib.request.urlopen(req, timeout=30)
    token = resp.headers.get("X-Subject-Token")
    print(f"  ✅ Токен получен!")
    
    # Получаем информацию о проекте
    body = json.loads(resp.read())
    print(f"  Проект: {body.get('token', {}).get('project', {}).get('name', 'unknown')}")
    
except urllib.error.HTTPError as e:
    print(f"  ❌ Ошибка получения токена: {e.code}")
    print(f"  Ответ: {e.read().decode()[:300]}")
    exit(1)
except Exception as e:
    print(f"  ❌ {e}")
    exit(1)

# Шаг 2: Создаём DNS зону
print("\n=== Шаг 2: Создаём DNS зону ===")

# Пробуем разные эндпоинты для DNS
dns_endpoints = [
    "https://api.selectel.ru/dns/v2/zones",
    "https://api.selectel.ru/dns/v1/zones",
    "https://dns.api.selectel.ru/v1/zones",
    "https://api.selectel.ru/domains/v1/zones",
]

zone_created = False
for endpoint in dns_endpoints:
    try:
        zone_data = json.dumps({
            "name": DOMAIN,
            "email": "dlyavsego02@mail.ru",
            "ttl": 300
        }).encode()
        
        headers = {
            "X-Auth-Token": token,
            "Content-Type": "application/json"
        }
        req = urllib.request.Request(endpoint, data=zone_data, headers=headers, method="POST")
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        print(f"  ✅ Зона создана через {endpoint}")
        print(f"  Ответ: {result}")
        zone_created = True
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 409:
            print(f"  ⚠️ Зона уже существует (409 Conflict)")
            zone_created = True
            break
        elif e.code == 404:
            print(f"  ❌ {endpoint}: 404 Not Found")
        else:
            print(f"  ❌ {endpoint}: {e.code} - {body[:200]}")

if not zone_created:
    print("\n⚠️ Не удалось создать зону через API.")
    print("Попробуем создать через панель управления Selectel вручную.")
    print("Или проверим, может зона уже создана...")
    
    # Проверяем существующие зоны
    for endpoint in dns_endpoints:
        try:
            headers = {"X-Auth-Token": token}
            req = urllib.request.Request(endpoint, headers=headers)
            resp = urllib.request.urlopen(req, timeout=30)
            zones = json.loads(resp.read())
            print(f"\n  Зоны через {endpoint}: {zones}")
            break
        except:
            pass

# Шаг 3: Добавляем A-записи (если зона создана)
print("\n=== Шаг 3: Добавляем A-записи ===")

# Пробуем добавить записи через разные эндпоинты
for endpoint in dns_endpoints:
    try:
        # Сначала получаем ID зоны
        headers = {"X-Auth-Token": token}
        req = urllib.request.Request(endpoint, headers=headers)
        resp = urllib.request.urlopen(req, timeout=30)
        zones = json.loads(resp.read())
        
        # Находим нашу зону
        zone_id = None
        if isinstance(zones, list):
            for z in zones:
                if z.get("name") == DOMAIN or z.get("name") == DOMAIN + ".":
                    zone_id = z["id"]
                    break
        elif isinstance(zones, dict):
            if zones.get("name") == DOMAIN:
                zone_id = zones["id"]
        
        if zone_id:
            print(f"  ✅ Найдена зона: id={zone_id}")
            
            # Добавляем A-записи
            records = [
                {"type": "A", "name": DOMAIN, "content": IP, "ttl": 300},
                {"type": "A", "name": f"www.{DOMAIN}", "content": IP, "ttl": 300}
            ]
            
            for r in records:
                try:
                    record_url = f"{endpoint}/{zone_id}/records"
                    record_data = json.dumps(r).encode()
                    headers2 = {"X-Auth-Token": token, "Content-Type": "application/json"}
                    req2 = urllib.request.Request(record_url, data=record_data, headers=headers2, method="POST")
                    resp2 = urllib.request.urlopen(req2, timeout=30)
                    print(f"  ✅ Запись {r['name']} -> {r['content']} создана")
                except urllib.error.HTTPError as e2:
                    if e2.code == 409:
                        print(f"  ⚠️ Запись {r['name']} уже существует")
                    else:
                        print(f"  ❌ {e2.code}: {e2.read().decode()[:200]}")
            break
    except:
        continue

print("\n=== Шаг 4: Проверяем DNS ===")
print("Ожидаем 30 секунд...")
time.sleep(30)

for name in [DOMAIN, f"www.{DOMAIN}"]:
    try:
        ip = socket.gethostbyname(name)
        print(f"  {name} -> {ip} {'✅' if ip == IP else '❌ не совпадает'}")
    except:
        print(f"  {name} -> NXDOMAIN ❌")

print("\n✅ Готово!")
