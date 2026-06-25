#!/usr/bin/env python3
"""Проверка статуса DNS для beklox.ru"""
import paramiko

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"

print("Подключаемся к серверу...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    return stdout.read().decode()

print("\n=== Проверка NS-серверов для beklox.ru ===")
print(run("dig NS beklox.ru +short 2>/dev/null || echo 'dig not available'"))

print("\n=== Проверка A-записи beklox.ru ===")
print(run("dig A beklox.ru +short 2>/dev/null || echo 'dig not available'"))

print("\n=== WHOIS beklox.ru (первые 20 строк) ===")
print(run("whois beklox.ru 2>/dev/null | head -20 || echo 'whois not available'"))

print("\n=== Проверка с Cloudflare DNS (1.1.1.1) ===")
print(run("dig @1.1.1.1 A beklox.ru +short 2>/dev/null || echo 'dig not available'"))

print("\n=== Проверка с Google DNS (8.8.8.8) ===")
print(run("dig @8.8.8.8 A beklox.ru +short 2>/dev/null || echo 'dig not available'"))

print("\n=== Статус Nginx ===")
print(run("nginx -t 2>&1"))

print("\n=== Слушает ли Nginx порт 80? ===")
print(run("ss -tlnp | grep -E ':(80|443) '"))

client.close()
print("\n✅ Проверка завершена")
