#!/usr/bin/env python3
"""Создаём DNS-зону для beklox.ru через API Selectel (финальная версия)"""
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
    print(f"  Токен: {token[:50]}...")
    
except urllib.error.HTTPError as e:
    print(f"  ❌ Ошибка получения токена: {e.code}")
    print(f"  Ответ: {e.read().decode()[:300]}")
    exit(1)
except Exception as e:
    print(f"  ❌ {e}")
    exit(1)

# Шаг 2: Получаем каталог сервисов (service catalog)
print("\n=== Шаг 2: Ищем DNS сервис ===")

try:
    url = "https://api.selectel.ru/identity/v3/auth/catalog"
    headers = {"X-Auth-Token": token}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=30)
    catalog = json.loads(resp.read())
    
    dns_endpoints = []
    for service in catalog.get("catalog", []):
        if "dns" in service.get("name", "").lower() or "dns" in service.get("type", "").lower():
            for ep in service.get("endpoints", []):
                dns_endpoints.append(ep.get("url"))
                print(f"  Найден DNS эндпоинт: {ep.get('url')}")
    
    if not dns_endpoints:
        print("  DNS сервис не найден в каталоге")
        print("  Доступные сервисы:")
        for s in catalog.get("catalog", []):
            print(f"    - {s.get('name')} ({s.get('type')})")
            for ep in s.get("endpoints", []):
                print(f"      {ep.get('interface')}: {ep.get('url')}")
except Exception as e:
    print(f"  ❌ {e}")

# Шаг 3: Пробуем создать DNS зону через разные эндпоинты
print("\n=== Шаг 3: Создаём DNS зону ===")

# Если не нашли DNS в каталоге, используем стандартные эндпоинты
if not dns_endpoints:
    dns_endpoints = [
        "https://api.selectel.ru/dns/v2",
        "https://api.selectel.ru/dns/v1",
        "https://api.selectel.ru/domains/v1",
    ]

zone_created = False
for base_url in dns_endpoints:
    zone_url = f"{base_url}/zones".replace("//zones", "/zones")
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
        req = urllib.request.Request(zone_url, data=zone_data, headers=headers, method="POST")
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        print(f"  ✅ Зона создана через {zone_url}")
        print(f"  Ответ: {json.dumps(result, indent=2)[:200]}")
        zone_created = True
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 409:
            print(f"  ⚠️ Зона уже существует (409)")
            zone_created = True
            break
        elif e.code == 404:
            print(f"  ❌ {zone_url}: 404")
        elif e.code == 401:
            print(f"  ❌ {zone_url}: 401 Unauthorized")
        else:
            print(f"  ❌ {zone_url}: {e.code} - {body[:200]}")

if not zone_created:
    print("\n⚠️ Не удалось создать зону через API.")
    print("Попробуйте создать DNS-зону вручную в панели Selectel:")
    print("1. Зайдите в https://my.selectel.ru")
    print("2. Перейдите в раздел 'Cloud DNS' или 'DNS-зоны'")
    print("3. Нажмите 'Создать зону'")
    print(f"4. Укажите домен: {DOMAIN}")
    print("5. Добавьте A-записи:")
    print(f"   - @ -> {IP}")
    print(f"   - www -> {IP}")
    exit(1)

# Шаг 4: Добавляем A-записи
print("\n=== Шаг 4: Добавляем A-записи ===")

for base_url in dns_endpoints:
    zone_url = f"{base_url}/zones".replace("//zones", "/zones")
    try:
        # Получаем список зон
        headers = {"X-Auth-Token": token}
        req = urllib.request.Request(zone_url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=30)
        zones = json.loads(resp.read())
        
        # Находим нашу зону
        zone_id = None
        zones_list = zones if isinstance(zones, list) else zones.get("zones", [])
        for z in zones_list:
            zname = z.get("name", "").rstrip(".")
            if zname == DOMAIN:
                zone_id = z["id"]
                break
        
        if zone_id:
            print(f"  ✅ Найдена зона: id={zone_id}")
            
            # Добавляем A-записи
            records_url = f"{base_url}/zones/{zone_id}/records".replace("//zones", "/zones")
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
    except:
        continue

print("\n=== Шаг 5: Проверяем DNS ===")
print("Ожидаем 30 секунд...")
time.sleep(30)

for name in [DOMAIN, f"www.{DOMAIN}"]:
    try:
        ip = socket.gethostbyname(name)
        print(f"  {name} -> {ip} {'✅' if ip == IP else '❌ не совпадает'}")
    except:
        print(f"  {name} -> NXDOMAIN ❌")

print("\n✅ Готово!")
