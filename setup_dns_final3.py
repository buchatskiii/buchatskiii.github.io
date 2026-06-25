#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru через API Selectel (работающая версия)"""
import urllib.request, json, time, socket

API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"
DOMAIN = "beklox.ru"
IP = "139.100.234.22"

BASE = "https://api.selectel.ru/domains/v1"
HEADERS = {"X-Token": API_KEY, "Content-Type": "application/json"}

def api(method, path, data=None):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]
    except Exception as e:
        return 0, str(e)

# Шаг 1: Создаём зону
print("=== Создаём DNS зону ===")
status, result = api("POST", "/", {
    "name": DOMAIN,
    "email": "dlyavsego02@mail.ru",
    "ttl": 300
})
print(f"  POST / -> {status}: {result}")

if status == 409:
    print("  ⚠️ Зона уже существует")
elif status != 200 and status != 201:
    print(f"  ❌ Ошибка: {result}")
    # Пробуем другой путь
    print("\nПробуем POST /zones...")
    status, result = api("POST", "/zones", {
        "name": DOMAIN,
        "email": "dlyavsego02@mail.ru",
        "ttl": 300
    })
    print(f"  POST /zones -> {status}: {result}")

# Получаем список зон
print("\n=== Получаем список зон ===")
status, result = api("GET", "/")
print(f"  GET / -> {status}: {result}")

# Находим ID зоны
zone_id = None
if isinstance(result, list):
    for z in result:
        if z.get("name") == DOMAIN:
            zone_id = z["id"]
            print(f"  ✅ Найдена зона: id={zone_id}")
            break

if not zone_id:
    print("  ❌ Зона не найдена")
    exit(1)

# Шаг 2: Добавляем A-записи
print("\n=== Добавляем A-записи ===")
records = [
    {"type": "A", "name": DOMAIN, "content": IP, "ttl": 300},
    {"type": "A", "name": f"www.{DOMAIN}", "content": IP, "ttl": 300}
]

for r in records:
    status, result = api("POST", f"/{zone_id}/records", r)
    if status == 409:
        print(f"  ⚠️ Запись {r['name']} уже существует")
    elif status in (200, 201):
        print(f"  ✅ Запись {r['name']} -> {r['content']} создана")
    else:
        print(f"  ❌ {r['name']}: {status} - {result}")

# Шаг 3: Проверяем DNS
print("\n=== Проверяем DNS ===")
print("Ожидаем 30 секунд...")
time.sleep(30)

for name in [DOMAIN, f"www.{DOMAIN}"]:
    try:
        ip = socket.gethostbyname(name)
        print(f"  {name} -> {ip} {'✅' if ip == IP else '❌ не совпадает'}")
    except:
        print(f"  {name} -> NXDOMAIN ❌")

print("\n✅ Готово!")
