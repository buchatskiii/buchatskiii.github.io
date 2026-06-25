#!/usr/bin/env python3
"""Принудительное обновление index.html на сервере"""
import paramiko, os

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
LOCAL_FILE = r"C:\Users\dlyav\Desktop\english-tutor\index.html"
REMOTE_FILE = "/var/www/englishpro/index.html"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
sftp = client.open_sftp()

# Читаем локальный файл
with open(LOCAL_FILE, 'rb') as f:
    data = f.read()

# Пишем на сервер через временный файл
tmp = REMOTE_FILE + ".tmp"
with sftp.open(tmp, 'wb') as f:
    f.write(data)
    f.flush()

# Переименовываем (атомарная операция)
sftp.rename(tmp, REMOTE_FILE)

print(f"Файл записан: {len(data)} байт")

# Проверяем
stdin, stdout, stderr = client.exec_command("grep -c 'EnglishBek' /var/www/englishpro/index.html 2>&1")
print(f"EnglishBek на сервере: {stdout.read().decode().strip()} раз")

stdin, stdout, stderr = client.exec_command("grep -c 'EnglishPro' /var/www/englishpro/index.html 2>&1")
print(f"EnglishPro на сервере: {stdout.read().decode().strip()} раз")

# Перезагружаем nginx
stdin, stdout, stderr = client.exec_command("systemctl reload nginx 2>&1")
print(stdout.read().decode())

sftp.close()
client.close()
print("Готово!")
