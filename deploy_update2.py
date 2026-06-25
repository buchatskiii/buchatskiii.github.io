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

print("Ищем где лежит сайт...")
print(run("find / -name 'index.html' -path '*/english*' 2>/dev/null"))
print(run("find / -name 'index.html' -path '*/beklox*' 2>/dev/null"))
print(run("ls -la /var/www/ 2>/dev/null"))
print(run("ls -la /var/www/html/ 2>/dev/null"))
print(run("cat /etc/nginx/sites-enabled/default 2>/dev/null"))
print(run("cat /etc/nginx/conf.d/*.conf 2>/dev/null"))
print(run("nginx -t 2>&1"))

client.close()
