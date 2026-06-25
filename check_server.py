#!/usr/bin/env python3
"""Проверяем что на сервере"""
import paramiko

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    return stdout.read().decode()

# Проверяем содержимое index.html на сервере
result = run("grep -n 'EnglishPro\\|EnglishBek' /var/www/englishpro/index.html 2>&1")
print("=== Поиск EnglishPro/Bek в index.html на сервере ===")
print(result or "❌ Ничего не найдено")

# Проверяем какой файл отдаёт Nginx
result = run("curl -s https://beklox.ru/ | grep -n 'EnglishPro\\|EnglishBek' 2>&1")
print("=== Что отдаёт Nginx ===")
print(result or "❌ Ничего не найдено")

# Проверяем конфиг Nginx
result = run("cat /etc/nginx/sites-enabled/default 2>/dev/null || cat /etc/nginx/conf.d/*.conf 2>/dev/null")
print("=== Nginx конфиг ===")
print(result)

client.close()
