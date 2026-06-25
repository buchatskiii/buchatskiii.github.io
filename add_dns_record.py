#!/usr/bin/env python3
"""Добавляем A-запись для beklox.ru через API Selectel"""
import requests
import json

SELECTEL_TOKEN = "SLb3f2e1a7c9d4e8f0a1b2c3d4e5f6a7b"
DOMAIN = "beklox.ru"
SERVER_IP = "139.100.234.22"

headers = {
    "X-Domain-Token": SELECTEL_TOKEN,
    "Content-Type": "application/json"
}

# 1. Получаем ID зоны
print("Получаем информацию о зоне...")
resp = requests.get(f"https://api.selectel.ru/domains/v1/{DOMAIN}", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
else:
    print(resp.text[:500])

# 2. Добавляем A-запись
print(f"\nДобавляем A-запись: {DOMAIN} -> {SERVER_IP}")
record_data = {
    "name": DOMAIN,
    "type": "A",
    "ttl": 300,
    "value": SERVER_IP
}

resp = requests.post(
    f"https://api.selectel.ru/domains/v1/{DOMAIN}/records",
    headers=headers,
    json=record_data
)
print(f"Status: {resp.status_code}")
if resp.status_code in [200, 201]:
    print("✅ A-запись добавлена!")
    print(resp.text[:300])
else:
    print(f"Ошибка: {resp.text[:500]}")

# 3. Добавляем www A-запись
print(f"\nДобавляем A-запись: www.{DOMAIN} -> {SERVER_IP}")
record_data = {
    "name": f"www.{DOMAIN}",
    "type": "A",
    "ttl": 300,
    "value": SERVER_IP
}

resp = requests.post(
    f"https://api.selectel.ru/domains/v1/{DOMAIN}/records",
    headers=headers,
    json=record_data
)
print(f"Status: {resp.status_code}")
if resp.status_code in [200, 201]:
    print("✅ A-запись для www добавлена!")
    print(resp.text[:300])
else:
    print(f"Ошибка: {resp.text[:500]}")

print("\n✅ Готово! DNS записи добавлены. Ожидайте распространения (обычно 5-15 минут)")
