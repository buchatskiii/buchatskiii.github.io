#!/usr/bin/env python3
"""Получаем SSL-сертификат Let's Encrypt для beklox.ru"""
import paramiko, time

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
DOMAIN = "beklox.ru"
APP_DIR = "/var/www/englishpro"

def run_cmd(client, command):
    stdin, stdout, stderr = client.exec_command(command, timeout=120)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    if error:
        print(f"  ⚠️  {error[:300]}")
    return output.strip()

print("=" * 50)
print("  Получение SSL-сертификата для beklox.ru")
print("=" * 50)

print("\n[1/4] Подключение к серверу...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
print("✅ Подключено")

# Сначала проверяем, что домен отвечает
print(f"\n[2/4] Проверка что {DOMAIN} отвечает...")
result = run_cmd(client, f"curl -s -o /dev/null -w '%{{http_code}}' http://{DOMAIN}/")
print(f"  HTTP {DOMAIN}/ -> {result}")

if result == "000":
    print("  ⚠️ Домен не отвечает, ждём 30 секунд...")
    time.sleep(30)
    result = run_cmd(client, f"curl -s -o /dev/null -w '%{{http_code}}' http://{DOMAIN}/")
    print(f"  HTTP {DOMAIN}/ -> {result}")

# Получаем сертификат
print(f"\n[3/4] Получение SSL-сертификата...")
print("  ⏳ Это может занять до 1 минуты...")
result = run_cmd(client, f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect 2>&1")
print(f"  Результат: {result[:500]}")

# Проверяем
print(f"\n[4/4] Проверка HTTPS...")
time.sleep(2)
result = run_cmd(client, f"curl -s -o /dev/null -w '%{{http_code}}' https://{DOMAIN}/")
print(f"  🌐 https://{DOMAIN}/ -> HTTP {result}")

result = run_cmd(client, f"curl -s -o /dev/null -w '%{{http_code}}' https://www.{DOMAIN}/")
print(f"  🌐 https://www.{DOMAIN}/ -> HTTP {result}")

result = run_cmd(client, f"curl -s -o /dev/null -w '%{{http_code}}' https://{DOMAIN}/api/")
print(f"  ⚙️  https://{DOMAIN}/api/ -> HTTP {result}")

client.close()

print("\n" + "=" * 50)
if result == "200":
    print("  ✅ SSL-сертификат получен!")
    print(f"  🌐 Сайт: https://{DOMAIN}")
    print(f"  🌐 Сайт: https://www.{DOMAIN}")
else:
    print("  ⚠️ Что-то пошло не так. Попробуйте позже.")
print("=" * 50)
