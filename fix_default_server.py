import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Добавляем default_server обратно, т.к. englishpro удалён
nginx_conf = """server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

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
print("✅ Nginx config с default_server")

# Проверяем
stdin, stdout, stderr = ssh.exec_command("nginx -t 2>&1")
result = stdout.read().decode()
print(result)

if 'successful' in result:
    ssh.exec_command("systemctl restart nginx")
    print("✅ Nginx перезапущен")
    
    # Проверяем что отвечает
    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost/")
    print(f"HTTP ответ: {stdout.read().decode()}")
else:
    print("❌ Ошибка!")

ssh.close()
