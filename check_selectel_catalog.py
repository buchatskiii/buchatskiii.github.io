#!/usr/bin/env python3
"""Проверяем каталог сервисов Selectel"""
import urllib.request, json

PROJECT_ID = "635e27ae-0b55-44ff-abc8-bf557c43076b"
API_KEY = "PLVWimjpS9VHQh1QL4FW8fXOV_625644"

# Получаем токен
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

url = "https://api.selectel.ru/identity/v3/auth/tokens"
req = urllib.request.Request(url, data=auth_data, headers={"Content-Type": "application/json"}, method="POST")
resp = urllib.request.urlopen(req, timeout=30)
token = resp.headers.get("X-Subject-Token")
print(f"Токен: {token[:50]}...")

# Пробуем получить каталог сервисов
url2 = "https://api.selectel.ru/identity/v3/auth/catalog"
req2 = urllib.request.Request(url2, headers={"X-Auth-Token": token})
resp2 = urllib.request.urlopen(req2, timeout=30)
catalog = json.loads(resp2.read())
print(f"\nКаталог сервисов ({len(catalog.get('catalog', []))} сервисов):")
for s in catalog.get("catalog", []):
    print(f"\n  {s.get('name')} ({s.get('type')})")
    for ep in s.get("endpoints", []):
        print(f"    {ep.get('interface')}: {ep.get('url')}")
