#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru через API Selectel"""
import urllib.request, json, time

PROJECT_ID = "635e27ae-0b55-44ff-abc8-bf557c43076b"
API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"
DOMAIN = "beklox.ru"
IP = "139.100.234.22"

def api_call(method, path, data=None):
    url = f"https://api.selectel.ru/domains/v1/{path}"
    headers = {
        "X-Domain-Token": API_KEY,
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ❌ {method} {path}: {e.code} - {body}")
        return None
    except Exception as e:
        print(f"  ❌ {method} {path}: {e}")
        return None

print("=== 1. Создаём DNS-зону ===")
zone_data = json.dumps({
    "name": DOMAIN,
    "type": "master",
    "email": "dlyavsego02@mail.ru",
    "ttl": 300
}).encode()

result = api_call("POST", "zones", zone_data)
if result:
    print(f"  ✅ Зона создана: {result}")
    zone_id = result.get("id")
else:
    # Возможно зона уже существует
    print("  ⚠️ Пробуем получить существующие зоны...")
    zones = api_call("GET", "zones")
    if zones:
        for z in zones:
            if z.get("name") == DOMAIN:
                zone_id = z["id"]
                print(f"  ✅ Зона уже существует: id={zone_id}")
                break
        else:
            print("  ❌ Не удалось создать зону")
            exit(1)
    else:
        print("  ❌ Не удалось получить зоны")
        exit(1)

print(f"\n=== 2. Добавляем A-записи ===")
records = [
    {"type": "A", "name": DOMAIN, "content": IP, "ttl": 300},
    {"type": "A", "name": f"www.{DOMAIN}", "content": IP, "ttl": 300}
]

for r in records:
    record_data = json.dumps(r).encode()
    result = api_call("POST", f"zones/{zone_id}/records", record_data)
    if result:
        print(f"  ✅ Запись {r['name']} -> {r['content']} создана")
    else:
        print(f"  ⚠️ Возможно запись уже существует")

print(f"\n=== 3. Проверяем DNS ===")
print("Ожидаем 30 секунд для распространения DNS...")
time.sleep(30)

import socket
for name in [DOMAIN, f"www.{DOMAIN}"]:
    try:
        ip = socket.gethostbyname(name)
        print(f"  {name} -> {ip} {'✅' if ip == IP else '❌ не совпадает'}")
    except:
        print(f"  {name} -> NXDOMAIN ❌")

print("\nГотово!")
