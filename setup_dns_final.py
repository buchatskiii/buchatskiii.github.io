#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru через API Selectel (X-Token работает!)"""
import urllib.request, json, time, socket

API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"
DOMAIN = "beklox.ru"
IP = "139.100.234.22"

BASE_URL = "https://api.selectel.ru/domains/v1"
HEADERS = {
    "X-Token": API_KEY,
    "Content-Type": "application/json"
}

def api(method, path, data=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:300]}
    except Exception as e:
        return {"error": str(e)}

# Шаг 1: Создаём зону
print("=== Создаём DNS зону ===")
result = api("POST", "/zones", {
    "name": DOMAIN,
    "email": "dlyavsego02@mail.ru",
    "ttl": 300
})
print(f"  Результат: {result}")

if isinstance(result, dict) and "error" in result:
    if result["error"] == 409:
        print("  ⚠️ Зона уже существует")
    else:
        print(f"  ❌ Ошибка: {result}")
        # Пробуем получить список зон
        print("\nПолучаем список зон...")
        zones = api("GET", "/zones")
        print(f"  Зоны: {zones}")
        exit(1)

zone_id = result.get("id") if isinstance(result, dict) else None
if not zone_id:
    # Пробуем найти зону в списке
    zones = api("GET", "/zones")
    if isinstance(zones, list):
        for z in zones:
            if z.get("name") == DOMAIN:
                zone_id = z["id"]
                print(f"  ✅ Найдена существующая зона: id={zone_id}")
                break

if not zone_id:
    print("  ❌ Не удалось получить ID зоны")
    exit(1)

# Шаг 2: Добавляем A-записи
print("\n=== Добавляем A-записи ===")
records = [
    {"type": "A", "name": DOMAIN, "content": IP, "ttl": 300},
    {"type": "A", "name": f"www.{DOMAIN}", "content": IP, "ttl": 300}
]

for r in records:
    result = api("POST", f"/zones/{zone_id}/records", r)
    if isinstance(result, dict) and "error" in result:
        if result["error"] == 409:
            print(f"  ⚠️ Запись {r['name']} уже существует")
        else:
            print(f"  ❌ {r['name']}: {result}")
    else:
        print(f"  ✅ Запись {r['name']} -> {r['content']} создана")

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
