#!/usr/bin/env python3
"""Проверяем DNS и получаем SSL-сертификат"""
import paramiko, time

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
DOMAIN = "beklox.ru"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    return stdout.read().decode()

print("=== Проверка A-записей ===")
for ns in ['a.ns.selectel.ru', 'b.ns.selectel.ru']:
    r1 = run(f"dig @{ns} {DOMAIN} A +short 2>&1").strip()
    r2 = run(f"dig @{ns} www.{DOMAIN} A +short 2>&1").strip()
    print(f"  {ns}:")
    print(f"    {DOMAIN} -> {r1 or '❌'}")
    print(f"    www.{DOMAIN} -> {r2 or '❌'}")

print(f"\n=== Проверка через curl (с сервера) ===")
r = run(f"curl -s -o /dev/null -w '%{{http_code}}' http://{DOMAIN}/ 2>&1")
print(f"  http://{DOMAIN}/ -> {r}")
r = run(f"curl -s -o /dev/null -w '%{{http_code}}' http://www.{DOMAIN}/ 2>&1")
print(f"  http://www.{DOMAIN}/ -> {r}")

# Если домен отвечает - получаем сертификат
if r != "000":
    print(f"\n=== Домен отвечает! Получаем SSL-сертификат... ===")
    result = run(f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect 2>&1")
    print(result[:500])
    
    time.sleep(2)
    r = run(f"curl -s -o /dev/null -w '%{{http_code}}' https://{DOMAIN}/ 2>&1")
    print(f"\n  https://{DOMAIN}/ -> {r}")
    r = run(f"curl -s -o /dev/null -w '%{{http_code}}' https://www.{DOMAIN}/ 2>&1")
    print(f"  https://www.{DOMAIN}/ -> {r}")
else:
    print("\n⚠️ Домен пока не отвечает. Нужно подождать распространения DNS.")

client.close()
