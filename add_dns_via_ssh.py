#!/usr/bin/env python3
"""Пробуем добавить A-запись через сервер, используя API Selectel v2"""
import paramiko
import requests
import json

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
DOMAIN = "beklox.ru"
TARGET_IP = "139.100.234.22"

# Пробуем через API Selectel v2 (другой эндпоинт)
print("Пробуем API Selectel v2...")
headers = {
    "Content-Type": "application/json",
    "X-Domain-Token": "SLb3f2e1a7c9d4e8f0a1b2c3d4e5f6a7b"
}

# Попробуем другой URL
urls = [
    f"https://api.selectel.ru/domains/v1/{DOMAIN}/records",
    f"https://api.selectel.ru/domains/v1/records/{DOMAIN}",
    f"https://api.selectel.ru/domains/v1/zones/{DOMAIN}/records",
]

for url in urls:
    print(f"\nПробуем GET {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Ответ: {resp.text[:500]}")
            break
        else:
            print(f"  {resp.text[:200]}")
    except Exception as e:
        print(f"  Ошибка: {e}")

# Пробуем через SSH - может на сервере есть API ключ?
print("\n\nПроверяем на сервере...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    return stdout.read().decode()

# Проверяем, может быть есть nsd или bind
print("\nПроверяем DNS серверы на сервере...")
print(run("which nsd bind named dnsmasq 2>/dev/null; dpkg -l 2>/dev/null | grep -i -E 'bind|nsd|dnsmasq' | head -5"))
print(run("ss -tlnp | grep 53 2>/dev/null || echo 'Нет DNS сервера на порту 53'"))

# Проверяем, может быть есть файл зоны
print("\nПроверяем файлы зон...")
print(run("find /etc -name '*beklox*' -o -name '*zone*' 2>/dev/null | head -10"))
print(run("find /var -name '*beklox*' 2>/dev/null | head -10"))

client.close()

print("\n\n=== ВЫВОД ===")
print("DNS делегирован на NS-сервера Selectel, но A-запись не создана.")
print("Нужно добавить A-запись вручную в панели управления Selectel:")
print(f"  1. Зайти в https://my.selectel.ru/domains")
print(f"  2. Выбрать домен beklox.ru")
print(f"  3. Добавить A-запись: @ -> {TARGET_IP}")
print(f"  4. Добавить A-запись: www -> {TARGET_IP}")
print(f"  5. Подождать 5-15 минут")
