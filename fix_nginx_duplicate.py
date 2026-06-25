import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Удаляем дублирующийся конфиг
stdin, stdout, stderr = ssh.exec_command("rm -f /etc/nginx/sites-enabled/englishpro")
print("✅ Удалён дублирующийся конфиг englishpro")

# Перезаписываем наш конфиг (без default_server, т.к. он уже есть в другом месте)
nginx_conf = """server {
    listen 80;
    listen [::]:80;
    server_name beklox.ru;

    # Статические файлы
    location /images/ {
        alias /var/www/englishpro/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /videos/ {
        alias /var/www/englishpro/videos/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        root /var/www/englishpro;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }
}
"""

stdin, stdout, stderr = ssh.exec_command("cat > /etc/nginx/sites-enabled/default << 'NGINX_EOF'\n" + nginx_conf + "\nNGINX_EOF")
print("✅ Nginx config перезаписан")

# Проверяем конфиг
stdin, stdout, stderr = ssh.exec_command("nginx -t 2>&1")
result = stdout.read().decode()
print(f"\n=== Проверка nginx -t ===")
print(result)

if 'successful' in result:
    ssh.exec_command("systemctl restart nginx")
    print("✅ Nginx перезапущен")
else:
    print("❌ Ошибка в конфиге!")

# Проверяем статус
stdin, stdout, stderr = ssh.exec_command("systemctl status nginx --no-pager -l 2>&1 | head -5")
print(f"\n=== Статус nginx ===")
print(stdout.read().decode())

ssh.close()
