#!/usr/bin/env python3
"""Настраиваем HTTPS на сервере через Let's Encrypt / Certbot"""
import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', username='root', password='qmc67Ra9TYas', timeout=30)

commands = """
set -e
echo "=== 1. Устанавливаем certbot ==="
apt-get update -qq
apt-get install -y -qq certbot python3-certbot-nginx 2>&1 | tail -3

echo ""
echo "=== 2. Получаем SSL-сертификат ==="
certbot --nginx -d 139.100.234.22 --non-interactive --agree-tos --email bek.english@example.com --redirect 2>&1 || true

echo ""
echo "=== 3. Проверяем результат ==="
ls -la /etc/letsencrypt/live/ 2>/dev/null || echo "No live dir"
nginx -t 2>&1 || true

echo ""
echo "=== 4. Перезагружаем nginx ==="
systemctl reload nginx 2>&1 || systemctl restart nginx 2>&1

echo ""
echo "=== 5. Проверяем HTTP(S) ==="
curl -s -o /dev/null -w "HTTP: %{http_code}\n" http://localhost/
curl -s -k -o /dev/null -w "HTTPS: %{http_code}\n" https://localhost/
"""

transport = client.get_transport()
channel = transport.open_session(timeout=120)
channel.exec_command('bash -c ' + repr(commands))
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
