#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru через API Selectel (упрощённая версия)"""
import urllib.request, json, time, socket

PROJECT_ID = "635e27ae-0b55-44ff-abc8-bf557c43076b"
API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"
DOMAIN = "beklox.ru"
IP = "139.100.234.22"

# Шаг 1: Получаем токен
print("=== Шаг 1: Получаем токен ===")
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
except Exception as e:
    print(f"  ❌ {e}")
    exit(1)

# Шаг 2: Пробуем разные эндпоинты для DNS
print("\n=== Шаг 2: Создаём DNS зону ===")

# Эндпоинты для DNS API Selectel
endpoints_to_try = [
    "https://api.selectel.ru/dns/v2/zones",
    "https://api.selectel.ru/dns/v1/zones", 
    "https://api.selectel.ru/domains/v1/zones",
    "https://api.selectel.ru/v1/dns/zones",
    "https://api.selectel.ru/v2/dns/zones",
]

zone_id = None
for endpoint in endpoints_to_try:
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
        print(f"  Ответ: {json.dumps(result, indent=2)[:300]}")
        
        # Извлекаем ID зоны
        if isinstance(result, dict):
            zone_id = result.get("id") or result.get("zone", {}).get("id")
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 409:
            print(f"  ⚠️ Зона уже существует на {endpoint}")
            # Пробуем получить ID существующей зоны
            try:
                req2 = urllib.request.Request(endpoint, headers={"X-Auth-Token": token})
                resp2 = urllib.request.urlopen(req2, timeout=30)
                zones = json.loads(resp2.read())
                zones_list = zones if isinstance(zones, list) else zones.get("zones", [])
                for z in zones_list:
                    if z.get("name", "").rstrip(".") == DOMAIN:
                        zone_id = z["id"]
                        print(f"  ✅ Найден ID существующей зоны: {zone_id}")
                        break
            except:
                pass
            break
        elif e.code == 404:
            print(f"  ❌ {endpoint}: 404")
        elif e.code == 401:
            print(f"  ❌ {endpoint}: 401")
        else:
            print(f"  ❌ {endpoint}: {e.code}")

if not zone_id:
    print("\n⚠️ Не удалось создать/найти зону через API.")
    print("Создайте DNS-зону вручную в панели Selectel:")
    print("1. https://my.selectel.ru → Cloud DNS → Создать зону")
    print(f"2. Домен: {DOMAIN}")
    print(f"3. A-запись: @ -> {IP}")
    print(f"4. A-запись: www -> {IP}")
    exit(1)

# Шаг 3: Добавляем A-записи
print("\n=== Шаг 3: Добавляем A-записи ===")

# Находим правильный base URL для records
for endpoint in endpoints_to_try:
    try:
        records_url = f"{endpoint}/{zone_id}/records"
        # Пробуем получить существующие записи
        req = urllib.request.Request(records_url, headers={"X-Auth-Token": token})
        resp = urllib.request.urlopen(req, timeout=30)
        existing = json.loads(resp.read())
        print(f"  ✅ Найден эндпоинт записей: {records_url}")
        
        # Добавляем A-записи
        records = [
            {"type": "A", "name": DOMAIN, "content": IP, "ttl": 300},
            {"type": "A", "name": f"www.{DOMAIN}", "content": IP, "ttl": 300}
        ]
        
        for r in records:
            try:
                record_data = json.dumps(r).encode()
                headers2 = {"X-Auth-Token": token, "Content-Type": "application/json"}
                req2 = urllib.request.Request(records_url, data=record_data, headers=headers2, method="POST")
                resp2 = urllib.request.urlopen(req2, timeout=30)
                print(f"  ✅ Запись {r['name']} -> {r['content']} создана")
            except urllib.error.HTTPError as e2:
                if e2.code == 409:
                    print(f"  ⚠️ Запись {r['name']} уже существует")
                else:
                    print(f"  ❌ {e2.code}: {e2.read().decode()[:200]}")
        break
    except urllib.error.HTTPError:
        continue
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
