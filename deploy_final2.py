#!/usr/bin/env python3
"""Обновление index.html через SSH командой"""
import paramiko

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
LOCAL_FILE = r"C:\Users\dlyav\Desktop\english-tutor\index.html"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)

# Читаем локальный файл
with open(LOCAL_FILE, 'rb') as f:
    content = f.read()

# Кодируем в base64 и передаём через SSH
import base64
encoded = base64.b64encode(content).decode()

cmd = f"echo '{encoded}' | base64 -d > /var/www/englishpro/index.html"
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
err = stderr.read().decode()
if err:
    print(f"Ошибка: {err}")
else:
    print("Файл записан!")

# Проверяем
stdin, stdout, stderr = client.exec_command("grep -c 'EnglishBek' /var/www/englishpro/index.html 2>&1")
print(f"EnglishBek: {stdout.read().decode().strip()}")

stdin, stdout, stderr = client.exec_command("grep -c 'EnglishPro' /var/www/englishpro/index.html 2>&1")
print(f"EnglishPro: {stdout.read().decode().strip()}")

# Перезагружаем nginx
stdin, stdout, stderr = client.exec_command("systemctl reload nginx 2>&1")
print(stdout.read().decode())

client.close()
print("Готово!")
