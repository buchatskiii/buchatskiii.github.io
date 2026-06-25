#!/usr/bin/env python3
"""Обновление сайта на сервере"""
import paramiko

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    return stdout.read().decode() + stderr.read().decode()

print("Обновляем сайт из GitHub...")
result = run("cd /var/www/englishpro && git pull origin master 2>&1")
print(result)

print("Перезагружаем Nginx...")
result = run("systemctl reload nginx 2>&1")
print(result)

print("Готово!")
client.close()
