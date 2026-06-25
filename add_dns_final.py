#!/usr/bin/env python3
"""Добавляем A-запись для beklox.ru через API Selectel с правильной авторизацией"""
import requests
import json

DOMAIN = "beklox.ru"
SERVER_IP = "139.100.234.22"

# Пробуем разные варианты авторизации
tokens_to_try = [
    ("X-Domain-Token", "SLb3f2e1a7c9d4e8f0a1b2c3d4e5f6a7b"),
    ("X-Domain-Token", "b3f2e1a7c9d4e8f0a1b2c3d4e5f6a7b"),
    ("Authorization", "Bearer SLb3f2e1a7c9d4e8f0a1b2c3d4e5f6a7b"),
    ("X-Token", "SLb3f2e1a7c9d4e8f0a1b2c3d4e5f6a7b"),
]

urls_to_try = [
    f"https://api.selectel.ru/domains/v1/{DOMAIN}",
    f"https://api.selectel.ru/domains/v1/{DOMAIN}/records",
    f"https://api.selectel.ru/domains/v1/zones/{DOMAIN}",
    f"https://api.selectel.ru/domains/v1/zones/{DOMAIN}/records",
]

print("Пробуем разные комбинации авторизации...")
found = False
for url in urls_to_try:
    for header_name, header_value in tokens_to_try:
        headers = {
            header_name: header_value,
            "Content-Type": "application/json"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                print(f"\n✅ Найдено! URL: {url}")
                print(f"   Header: {header_name}: {header_value[:20]}...")
                print(f"   Ответ: {resp.text[:500]}")
                found = True
                break
        except:
            pass
    if found:
        break

if not found:
    print("\n❌ API не отвечает. Возможно, у Selectel другой API.")
    print("\nПробуем через панель управления Selectel (REST API v2)...")
    
    # Попробуем API v2 Selectel
    headers = {
        "Content-Type": "application/json",
        "X-Domain-Token": "SLb3f2e1a7c9d4e8f0a1b2c3d4e5f6a7b"
    }
    
    # API для DNS
    dns_urls = [
        f"https://api.selectel.ru/dns/v1/{DOMAIN}",
        f"https://api.selectel.ru/dns/v1/zones/{DOMAIN}",
        f"https://api.selectel.ru/dns/v1/domain/{DOMAIN}",
    ]
    
    for url in dns_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            print(f"  {url} -> {resp.status_code}")
            if resp.status_code == 200:
                print(f"  ✅ {resp.text[:300]}")
                found = True
                break
        except Exception as e:
            print(f"  {url} -> Error: {e}")

if not found:
    print("\n\n=== ИНСТРУКЦИЯ ===")
    print("API Selectel не отвечает на наши токены.")
    print("Нужно добавить A-запись вручную в панели управления Selectel:")
    print(f"  1. Откройте https://my.selectel.ru/domains")
    print(f"  2. Войдите в аккаунт Selectel")
    print(f"  3. Выберите домен beklox.ru")
    print(f"  4. Нажмите «Управление DNS» или «DNS-записи»")
    print(f"  5. Добавьте A-запись:")
    print(f"     - Имя: @ (или оставить пустым)")
    print(f"     - Тип: A")
    print(f"     - Значение: {SERVER_IP}")
    print(f"     - TTL: 300")
    print(f"  6. Добавьте A-запись для www:")
    print(f"     - Имя: www")
    print(f"     - Тип: A")
    print(f"     - Значение: {SERVER_IP}")
    print(f"     - TTL: 300")
    print(f"  7. Сохраните и подождите 5-15 минут")
    print(f"\nПосле этого сайт будет доступен по адресу: http://beklox.ru")
    print(f"Затем запустите: python setup_ssl_letsencrypt.py")
