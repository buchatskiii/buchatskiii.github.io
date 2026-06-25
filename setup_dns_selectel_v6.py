#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru через API Selectel"""
import urllib.request, json, time, socket

PROJECT_ID = "635e27ae-0b55-44ff-abc8-bf557c43076b"
API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"
DOMAIN = "beklox.ru"
IP = "139.100.234.22"

def api_request(method, url, data=None, token=None):
    headers = {}
    if token:
        headers["X-Auth-Token"] = token
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        body = resp.read()
        if body:
            return json.loads(body)
        return {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": e.code, "body": body[:300]}
    except Exception as e:
        return {"error": str(e)}

# Шаг 1: Получаем токен
print("=== Шаг 1: Получаем токен ===")
auth_data = {
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
}

url = "https://api.selectel.ru/identity/v3/auth/tokens"
req = urllib.request.Request(url, data=json.dumps(auth_data).encode(), 
                            headers={"Content-Type": "application/json"}, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=30)
    token = resp.headers.get("X-Subject-Token")
    print(f"  ✅ Токен получен!")
except Exception as e:
    print(f"  ❌ {e}")
    exit(1)

# Шаг 2: Пробуем разные эндпоинты
print("\n=== Шаг 2: Создаём DNS зону ===")

endpoints = [
    "https://api.selectel.ru/dns/v2/zones",
    "https://api.selectel.ru/dns/v1/zones",
    "https://api.selectel.ru/domains/v1/zones",
]

zone_id = None
for ep in endpoints:
    # Сначала пробуем получить список зон
    result = api_request("GET", ep, token=token)
    if isinstance(result, dict) and "error" not in result:
        zones = result.get("zones", result.get("domains", []))
        if isinstance(zones, list):
            for z in zones:
                if z.get("name", "").rstrip(".") == DOMAIN:
                    zone_id = z["id"]
                    print(f"  ✅ Зона уже существует: id={zone_id}")
                    break
        if zone_id:
            break
    
    # Создаём зону
    zone_data = {
        "name": DOMAIN,
        "email": "dlyavsego02@mail.ru",
        "ttl": 300
    }
    result = api_request("POST", ep, data=zone_data, token=token)
    
    if isinstance(result, dict):
        if "error" not in result:
            zone_id = result.get("id")
            print(f"  ✅ Зона создана через {ep}: id={zone_id}")
            break
        elif result.get("error") == 409:
            print(f"  ⚠️ Зона уже существует на {ep}")
            # Получаем ID
            result2 = api_request("GET", ep, token=token)
            if isinstance(result2, dict):
                zones = result2.get("zones", result2.get("domains", []))
                if isinstance(zones, list):
                    for z in zones:
                        if z.get("name", "").rstrip(".") == DOMAIN:
                            zone_id = z["id"]
                            print(f"  ✅ ID зоны: {zone_id}")
                            break
            if zone_id:
                break
        elif result.get("error") == 404:
            print(f"  ❌ {ep}: 404")
        elif result.get("error") == 401:
            print(f"  ❌ {ep}: 401")
        else:
            print(f"  ❌ {ep}: {result}")

if not zone_id:
    print("\n⚠️ Не удалось создать зону через API.")
    print("Создайте DNS-зону вручную в панели Selectel:")
    print("1. https://my.selectel.ru → Cloud DNS → Создать зону")
    print(f"2. Домен: {DOMAIN}")
    print(f"3. A-запись: @ -> {IP}")
    print(f"4. A-запись: www -> {IP}")
    exit(1)

# Шаг 3: Добавляем A-записи
print("\n=== Шаг 3: Добавляем A-записи ===")

for ep in endpoints:
    records_url = f"{ep}/{zone_id}/records"
    result = api_request("GET", records_url, token=token)
    
    if isinstance(result, dict) and "error" not in result:
        print(f"  ✅ Найден эндпоинт: {records_url}")
        
        records = [
            {"type": "A", "name": DOMAIN, "content": IP, "ttl": 300},
            {"type": "A", "name": f"www.{DOMAIN}", "content": IP, "ttl": 300}
        ]
        
        for r in records:
            result = api_request("POST", records_url, data=r, token=token)
            if isinstance(result, dict):
                if "error" not in result:
                    print(f"  ✅ Запись {r['name']} -> {r['content']} создана")
                elif result.get("error") == 409:
                    print(f"  ⚠️ Запись {r['name']} уже существует")
                else:
                    print(f"  ❌ {r['name']}: {result}")
        break
    elif isinstance(result, dict) and result.get("error") == 404:
        continue
    else:
        print(f"  ❌ {records_url}: {result}")

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
