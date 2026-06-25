#!/usr/bin/env python3
"""Настройка Nginx для домена beklox.ru и получение SSL-сертификата Let's Encrypt"""
import paramiko, os, time

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
APP_DIR = "/var/www/englishpro"
DOMAIN = "beklox.ru"

def run_cmd(client, command, sudo=False):
    """Выполнить команду на сервере"""
    if sudo:
        command = f"sudo {command}"
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    if exit_status != 0 and error:
        print(f"  ⚠️  {error[:300]}")
    return output.strip()

print("=" * 50)
print("  Настройка домена beklox.ru и SSL")
print("=" * 50)

print("\n[1/6] Подключение к серверу...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
print("✅ Подключено")

# Проверяем, что DNS уже резолвится
print("\n[2/6] Проверка DNS...")
result = run_cmd(client, f"dig +short {DOMAIN} 2>/dev/null || nslookup {DOMAIN} 2>/dev/null | grep Address")
print(f"  DNS: {result or 'ожидание распространения...'}")

# Устанавливаем certbot
print("\n[3/6] Установка certbot...")
run_cmd(client, "apt-get update -qq 2>/dev/null")
run_cmd(client, "apt-get install -y -qq certbot python3-certbot-nginx 2>/dev/null")
print("✅ Certbot установлен")

# Создаём конфиг Nginx для домена (HTTP-only для получения сертификата)
print("\n[4/6] Настройка Nginx для домена...")
nginx_config = f"""server {{
    listen 80;
    server_name {DOMAIN} www.{DOMAIN};

    root {APP_DIR};
    index index.html;

    location / {{
        try_files $uri $uri/ /index.html;
    }}

    location /images/ {{
        alias {APP_DIR}/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}

    location /api/ {{
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
run_cmd(client, f"cat > /etc/nginx/sites-available/englishpro << 'NGINXEOF'\n{nginx_config}\nNGINXEOF")
run_cmd(client, "ln -sf /etc/nginx/sites-available/englishpro /etc/nginx/sites-enabled/")
run_cmd(client, "nginx -t")
run_cmd(client, "systemctl reload nginx")
print("✅ Nginx настроен на HTTP")

# Получаем SSL-сертификат
print(f"\n[5/6] Получение SSL-сертификата для {DOMAIN}...")
print("  ⏳ Это может занять до 30 секунд...")
result = run_cmd(client, f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect 2>&1")
print(f"  Результат: {result[:500]}")

# Проверяем результат
print("\n[6/6] Проверка...")
time.sleep(2)
result = run_cmd(client, f"curl -s -o /dev/null -w '%{{http_code}}' https://{DOMAIN}/")
print(f"  🌐 https://{DOMAIN}/ -> HTTP {result}")

result = run_cmd(client, f"curl -s -o /dev/null -w '%{{http_code}}' https://{DOMAIN}/api/")
print(f"  ⚙️  https://{DOMAIN}/api/ -> HTTP {result}")

client.close()

print("\n" + "=" * 50)
print("  ✅ Настройка завершена!")
print(f"  🌐 Сайт: https://{DOMAIN}")
print(f"  ⚙️  API:  https://{DOMAIN}/api")
print("=" * 50)
