#!/usr/bin/env python3
"""Проверяем и настраиваем DNS-сервера для beklox.ru"""
import paramiko

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
DOMAIN = "beklox.ru"

print("Подключаемся к серверу...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    return stdout.read().decode()

print("\n=== Текущие NS-записи beklox.ru ===")
print(run(f"dig NS {DOMAIN} +short 2>&1"))

print("\n=== WHOIS информация ===")
print(run(f"whois {DOMAIN} 2>/dev/null | grep -E 'nserver:|state:'"))

print("\n=== Проверка A-записи ===")
print(run(f"dig A {DOMAIN} +short 2>&1"))

print("\n=== Проверка через NS-сервера Selectel ===")
for ns in ['a.ns.selectel.ru', 'b.ns.selectel.ru', 'c.ns.selectel.ru', 'd.ns.selectel.ru']:
    result = run(f"dig @{ns} {DOMAIN} A +short 2>&1")
    print(f"  {ns}: {result.strip() or 'нет записи'}")

client.close()

print("\n\n=== ИНСТРУКЦИЯ ===")
print("Сейчас в панели управления доменом (у регистратора) должны быть указаны")
print("NS-сервера Selectel. Их должно быть минимум 2:")
print("  a.ns.selectel.ru")
print("  b.ns.selectel.ru")
print("  (можно также c.ns.selectel.ru и d.ns.selectel.ru)")
print()
print("После этого в панели управления DNS Selectel нужно добавить A-записи:")
print(f"  @ -> {SERVER_IP}")
print(f"  www -> {SERVER_IP}")
