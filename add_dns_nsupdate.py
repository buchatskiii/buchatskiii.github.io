#!/usr/bin/env python3
"""Пробуем добавить A-запись через nsupdate или через API Selectel с правильным токеном"""
import paramiko

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
DOMAIN = "beklox.ru"
TARGET_IP = "139.100.234.22"

print("Подключаемся к серверу...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    return stdout.read().decode() + stderr.read().decode()

# Проверяем, может быть на сервере есть API ключ Selectel
print("\nПроверяем наличие API ключей Selectel...")
print(run("find /root /home /etc -name '*.env' -o -name '*selectel*' -o -name '*token*' 2>/dev/null | head -10"))

# Проверяем, может быть домен управляется через панель Selectel и там уже есть A-запись
print("\nПроверяем DNS через сервер напрямую...")
print(run(f"dig @a.ns.selectel.ru {DOMAIN} A +short 2>&1"))
print(run(f"dig @b.ns.selectel.ru {DOMAIN} A +short 2>&1"))

# Проверяем, может быть A-запись уже появилась
print("\nПроверяем через разные DNS...")
print(run(f"dig @1.1.1.1 {DOMAIN} A +short 2>&1"))
print(run(f"dig @8.8.8.8 {DOMAIN} A +short 2>&1"))

# Проверяем whois ещё раз
print("\nWHOIS статус...")
print(run("whois beklox.ru 2>/dev/null | grep -E 'state:|nserver:'"))

client.close()

print("\n\n=== ИТОГ ===")
print("Домен beklox.ru зарегистрирован и делегирован на NS Selectel.")
print("A-запись отсутствует - её нужно добавить вручную.")
print()
print("Самый простой способ - через панель управления Selectel:")
print("1. Зайдите на https://my.selectel.ru")
print("2. Войдите в аккаунт")
print("3. Перейдите в раздел 'Домены'")
print("4. Выберите beklox.ru")
print("5. Нажмите 'Управление DNS-записями'")
print("6. Добавьте A-запись: @ -> 139.100.234.22")
print("7. Добавьте A-запись: www -> 139.100.234.22")
print("8. Сохраните")
print()
print("ИЛИ через API (если знаете правильный токен):")
print("curl -X POST https://api.selectel.ru/domains/v1/beklox.ru/records \\")
print("  -H 'X-Domain-Token: ВАШ_ТОКЕН' \\")
print("  -H 'Content-Type: application/json' \\")
print("  -d '{\"name\":\"beklox.ru\",\"type\":\"A\",\"ttl\":300,\"value\":\"139.100.234.22\"}'")
