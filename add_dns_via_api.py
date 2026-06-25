#!/usr/bin/env python3
"""Добавляем A-запись для beklox.ru через API Selectel"""
import requests

DOMAIN = "beklox.ru"
SERVER_IP = "139.100.234.22"
TOKEN = "SLb3f2e1a7c9d4e8f0a1b2c3d4e5f6a7b"

headers = {
    "X-Domain-Token": TOKEN,
    "Content-Type": "application/json"
}

# Пробуем разные эндпоинты
endpoints = [
    f"https://api.selectel.ru/domains/v1/{DOMAIN}/records",
    f"https://api.selectel.ru/domains/v1/zones/{DOMAIN}/records",
    f"https://api.selectel.ru/domains/v1/{DOMAIN}/dns/records",
    f"https://api.selectel.ru/domains/v1/zones/{DOMAIN}/dns/records",
]

for ep in endpoints:
    try:
        resp = requests.get(ep, headers=headers, timeout=10)
        ct = resp.headers.get("Content-Type", "")
        print(f"{resp.status_code} {ep}")
        print(f"  Content-Type: {ct}")
        if "json" in ct:
            print(f"  Data: {resp.text[:300]}")
        elif resp.status_code == 200:
            print(f"  Body: {resp.text[:200]}")
    except Exception as e:
        print(f"ERR {ep}: {e}")
