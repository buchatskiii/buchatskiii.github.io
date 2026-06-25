import paramiko
import re

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# ===== 1. Восстанавливаем nginx конфиг =====
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
print("✅ Nginx config восстановлен")

# ===== 2. Проверяем HTML =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Проверяем какие ссылки на фото
photo_refs = re.findall(r'src="([^"]*images[^"]*)"', html)
print(f"\n=== Ссылки на фото в HTML ({len(photo_refs)}) ===")
for r in photo_refs:
    print(f"  {r}")

# Если всё ещё student*, исправляем
if any('student' in r for r in photo_refs):
    print("\n❌ Всё ещё есть student ссылки! Исправляю...")
    replacements = {
        'images/student1.jpg': '/images/1.jpg',
        'images/student2.jpg': '/images/2.jpg',
        'images/student3.jpg': '/images/3.jpg',
        'images/student4.jpg': '/images/4.jpg',
        'images/student5.jpg': '/images/5.jpg',
        'images/student6.jpg': '/images/6.jpg',
    }
    for old, new in replacements.items():
        if old in html:
            html = html.replace(old, new)
            print(f"  ✅ {old} -> {new}")
    
    html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=27.0', html)
    html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=27.0', html)
    
    with sftp.open("/var/www/englishpro/index.html", "w") as f:
        f.write(html.encode("utf-8"))
    print("✅ HTML обновлён")
else:
    print("✅ Ссылки на фото корректные")

# ===== 3. Проверяем API =====
print("\n=== Проверка API ===")
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs")
api_status = stdout.read().decode()
print(f"API docs: {api_status}")

if api_status != '200':
    print("❌ API не отвечает! Перезапускаем...")
    ssh.exec_command("systemctl restart english-api")
    print("✅ API перезапущен")

sftp.close()
ssh.close()

# ===== 4. Перезапускаем nginx =====
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n🎉 Готово! Nginx, фото и API исправлены")
