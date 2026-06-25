#!/usr/bin/env python3
"""Проверяем DNS для beklox.ru"""
import paramiko

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
DOMAIN = "beklox.ru"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    return stdout.read().decode()

print("=== Проверка A-записи через разные NS-сервера ===")
for ns in ['a.ns.selectel.ru', 'b.ns.selectel.ru', 'c.ns.selectel.ru', 'd.ns.selectel.ru']:
    result = run(f"dig @{ns} {DOMAIN} A +short 2>&1")
    print(f"  {ns}: {result.strip() or '❌ нет A-записи'}")

print(f"\n=== Проверка www.{DOMAIN} ===")
for ns in ['a.ns.selectel.ru', 'b.ns.selectel.ru']:
    result = run(f"dig @{ns} www.{DOMAIN} A +short 2>&1")
    print(f"  {ns}: {result.strip() or '❌ нет A-записи'}")

print(f"\n=== Проверка через публичные DNS ===")
result = run(f"dig @1.1.1.1 {DOMAIN} A +short 2>&1")
print(f"  Cloudflare: {result.strip() or '❌ нет записи'}")
result = run(f"dig @8.8.8.8 {DOMAIN} A +short 2>&1")
print(f"  Google: {result.strip() or '❌ нет записи'}")

print(f"\n=== WHOIS ===")
print(run(f"whois {DOMAIN} 2>/dev/null | grep -E 'nserver:|state:'"))

client.close()

print("\n\n=== ВЫВОД ===")
print("Если A-запись не найдена ни на одном NS-сервере,")
print("значит её нужно добавить в панели управления Selectel.")
print()
print("Как добавить A-запись в панели Selectel:")
print("1. https://my.selectel.ru → Домены → beklox.ru")
print("2. Нажмите «Управление DNS» или «DNS-записи»")
print("3. Нажмите «Добавить запись»")
print("4. Тип: A, Имя: @, Значение: 139.100.234.22, TTL: 300")
print("5. Нажмите «Добавить запись»")
print("6. Ещё раз: Тип: A, Имя: www, Значение: 139.100.234.22, TTL: 300")
print("7. Сохраните")
