#!/usr/bin/env python3
"""Загружаем исправленный index.html на сервер"""
import paramiko, os

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
APP_DIR = "/var/www/englishpro"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

print("Подключаемся к серверу...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
print("✅ Подключено")

print("\nЗагружаем index.html...")
sftp = client.open_sftp()
sftp.put(os.path.join(LOCAL_DIR, "index.html"), f"{APP_DIR}/index.html")
sftp.close()
print("✅ index.html загружен")

# Перезапускаем Nginx
stdin, stdout, stderr = client.exec_command("systemctl restart nginx")
stdout.channel.recv_exit_status()
print("✅ Nginx перезапущен")

client.close()
print("\n✅ Готово! Исправлен id чекбокса: privacyCheck -> privacy")
