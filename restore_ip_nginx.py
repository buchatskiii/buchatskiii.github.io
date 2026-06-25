#!/usr/bin/env python3
"""Восстанавливаем Nginx для работы по IP, пока DNS не распространится"""
import paramiko

SERVER_IP = "139.100.234.22"
SERVER_USER = "root"
SERVER_PASS = "qmc67Ra9TYas"
APP_DIR = "/var/www/englishpro"

print("Подключаемся к серверу...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASS)
print("✅ Подключено")

# Восстанавливаем конфиг для работы по IP
nginx_config = f"""server {{
    listen 80;
    server_name {SERVER_IP} beklox.ru www.beklox.ru;

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
stdin, stdout, stderr = client.exec_command(f"cat > /etc/nginx/sites-available/englishpro << 'NGINXEOF'\n{nginx_config}\nNGINXEOF")
stdout.channel.recv_exit_status()

stdin, stdout, stderr = client.exec_command("nginx -t && systemctl reload nginx")
print(stdout.read().decode())

client.close()
print("\n✅ Nginx восстановлен для работы по IP и домену (когда DNS распространится)")
print(f"🌐 Сайт доступен по: https://{SERVER_IP}")
