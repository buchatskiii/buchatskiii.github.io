#!/usr/bin/env python3
"""Настраиваем SSL через certbot для домена beklox.ru"""
import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', username='root', password='qmc67Ra9TYas', timeout=30)

script = """#!/bin/bash
set -e

echo "=== 1. Обновляем конфиг nginx для домена beklox.ru ==="
cat > /etc/nginx/sites-available/englishpro << 'NGINX_CONF'
server {
    listen 80;
    server_name beklox.ru www.beklox.ru 139.100.234.22;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name beklox.ru www.beklox.ru 139.100.234.22;

    ssl_certificate /etc/nginx/ssl/englishpro.crt;
    ssl_certificate_key /etc/nginx/ssl/englishpro.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/englishpro;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
NGINX_CONF

echo "Конфиг обновлён"

echo ""
echo "=== 2. Проверяем nginx ==="
nginx -t

echo ""
echo "=== 3. Перезагружаем nginx ==="
systemctl reload nginx || systemctl restart nginx

echo ""
echo "=== 4. Запускаем certbot ==="
certbot --nginx -d beklox.ru -d www.beklox.ru --non-interactive --agree-tos --email bek.english@example.com --redirect 2>&1

echo ""
echo "=== 5. Результат ==="
nginx -t 2>&1
systemctl reload nginx 2>&1 || systemctl restart nginx 2>&1

echo ""
echo "=== 6. Проверка ==="
curl -s -o /dev/null -w "HTTP: %{http_code}\\n" http://localhost/
curl -s -k -o /dev/null -w "HTTPS: %{http_code}\\n" https://localhost/

echo ""
echo "Готово!"
"""

stdin, stdout, stderr = client.exec_command('cat > /tmp/setup_ssl_domain.sh', timeout=10)
stdin.write(script)
stdin.channel.shutdown_write()
time.sleep(1)

client.exec_command('chmod +x /tmp/setup_ssl_domain.sh', timeout=10)
time.sleep(1)

transport = client.get_transport()
channel = transport.open_session(timeout=120)
channel.exec_command('bash /tmp/setup_ssl_domain.sh')
time.sleep(60)

out = b''
while channel.recv_ready():
    out += channel.recv(4096)
while channel.recv_stderr_ready():
    _ = channel.recv_stderr(4096)

print(out.decode('utf-8', errors='replace'))
channel.close()
client.close()
print('Done!')
