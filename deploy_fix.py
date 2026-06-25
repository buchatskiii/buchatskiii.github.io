#!/usr/bin/env python3
"""Быстрый деплой исправленного script.js на сервер"""
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

print("\nЗагружаем script.js...")
sftp = client.open_sftp()
sftp.put(os.path.join(LOCAL_DIR, "script.js"), f"{APP_DIR}/script.js")
sftp.close()
print("✅ script.js загружен")

# Перезапускаем Nginx (на всякий случай)
stdin, stdout, stderr = client.exec_command("systemctl restart nginx")
stdout.channel.recv_exit_status()
print("✅ Nginx перезапущен")

client.close()
print("\n✅ Готово! Форма теперь будет отправляться через относительный путь /api/lead")
