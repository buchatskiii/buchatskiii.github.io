#!/usr/bin/env python3
"""Проверяем .env на сервере и настраиваем Telegram бота"""
import paramiko, os

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
APP_DIR = "/var/www/englishpro"

print("Подключаемся к серверу...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
print("✅ Подключено")

# Проверяем .env
print("\nПроверяем .env на сервере...")
stdin, stdout, stderr = client.exec_command(f"cat {APP_DIR}/.env")
env_content = stdout.read().decode()
print(f"Содержимое .env:\n{env_content}")

# Проверяем статус сервиса
print("\nПроверяем статус API сервиса...")
stdin, stdout, stderr = client.exec_command("systemctl status englishpro-api 2>&1 | head -20")
print(stdout.read().decode())

# Проверяем, что API отвечает локально
print("\nПроверяем API локально...")
stdin, stdout, stderr = client.exec_command("curl -s http://127.0.0.1:8000/")
print(f"GET /: {stdout.read().decode()}")

stdin, stdout, stderr = client.exec_command("curl -s -X POST http://127.0.0.1:8000/api/lead -H 'Content-Type: application/json' -d '{\"name\":\"Тест\",\"phone\":\"+79991234567\",\"email\":\"test@test.com\",\"goal\":\"ege\",\"message\":\"\",\"privacy\":true}'")
print(f"POST /api/lead: {stdout.read().decode()}")

client.close()
print("\n✅ Проверка завершена")
