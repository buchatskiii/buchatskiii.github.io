import paramiko
import os

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Создаём папку для видео на сервере
stdin, stdout, stderr = ssh.exec_command("mkdir -p /var/www/englishpro/videos")
print("mkdir:", stdout.read().decode(), stderr.read().decode())

# Настраиваем Nginx для поддержки больших файлов и streaming video
nginx_config = """server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    root /var/www/englishpro;
    index index.html;

    client_max_body_size 500M;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /images/ {
        alias /var/www/englishpro/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /videos/ {
        alias /var/www/englishpro/videos/;
        expires 7d;
        add_header Cache-Control "public, immutable";
        add_header Accept-Ranges bytes;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}

server {
    server_name beklox.ru www.beklox.ru;

    root /var/www/englishpro;
    index index.html;

    client_max_body_size 500M;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /images/ {
        alias /var/www/englishpro/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /videos/ {
        alias /var/www/englishpro/videos/;
        expires 7d;
        add_header Cache-Control "public, immutable";
        add_header Accept-Ranges bytes;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/beklox.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beklox.ru/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = www.beklox.ru) {
        return 301 https://$host$request_uri;
    }

    if ($host = beklox.ru) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name beklox.ru www.beklox.ru;
    return 404;
}
"""

sftp = ssh.open_sftp()
with sftp.open("/etc/nginx/sites-available/englishpro", "w") as f:
    f.write(nginx_config)
sftp.close()
print("Nginx config updated")

# Reload nginx
stdin, stdout, stderr = ssh.exec_command("nginx -t && nginx -s reload")
print("Nginx reload:", stdout.read().decode(), stderr.read().decode())

ssh.close()

print("\n✅ Папка /videos/ создана на сервере!")
print("✅ Nginx настроен для поддержки видео до 500MB")
print()
print("📹 КАК ЗАГРУЗИТЬ ВИДЕО:")
print("=" * 50)
print("1. Положите ваш MP4 файл в папку english-tutor/videos/")
print("   Например: english-tutor/videos/presentation.mp4")
print()
print("2. Запустите эту команду для загрузки на сервер:")
print("   python upload_video_file.py")
print()
print("3. Вставьте на сайт HTML-код:")
print('   <video width="100%" controls>')
print('     <source src="/videos/presentation.mp4" type="video/mp4">')
print("   </video>")
print()
print("📌 РЕКОМЕНДАЦИИ ПО ВИДЕО:")
print("- Формат: MP4 (H.264 кодек)")
print("- Максимальный размер: 500MB")
print("- Разрешение: 1920x1080 или 1280x720")
print("- Для конвертации используйте: https://handbrake.fr")
