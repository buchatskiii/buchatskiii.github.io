#!/usr/bin/env python3
"""Копируем обновлённые файлы на сервер"""
import paramiko
import os

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
LOCAL_DIR = r"C:\Users\dlyav\Desktop\english-tutor"
REMOTE_DIR = "/var/www/englishpro"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
sftp = client.open_sftp()

files_to_copy = ["index.html", "styles.css", "script.js", "privacy.html", "offer.html", "consent.html"]

for fname in files_to_copy:
    local_path = os.path.join(LOCAL_DIR, fname)
    remote_path = os.path.join(REMOTE_DIR, fname)
    if os.path.exists(local_path):
        sftp.put(local_path, remote_path)
        print(f"✅ {fname} -> скопирован")
    else:
        print(f"❌ {fname} -> не найден локально")

sftp.close()

# Перезагружаем Nginx
stdin, stdout, stderr = client.exec_command("systemctl reload nginx 2>&1")
print(stdout.read().decode())

client.close()
print("\n✅ Готово! Сайт обновлён.")
