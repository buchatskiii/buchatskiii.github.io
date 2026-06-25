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

# ===== 1. Читаем HTML и смотрим какие ссылки на фото =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Ищем все unsplash ссылки
unsplash_urls = re.findall(r'https://images\.unsplash\.com[^"\']+', html)
print("=== Unsplash ссылки в HTML ===")
for u in unsplash_urls:
    print(f"  {u[:80]}...")

# ===== 2. Заменяем все unsplash ссылки на локальные =====
# Собираем все уникальные unsplash ссылки
all_unsplash = set(re.findall(r'https://images\.unsplash\.com[^"\']+', html))
print(f"\nНайдено {len(all_unsplash)} unsplash ссылок")

# Заменяем их все на /images/ с номером
# Но сначала посмотрим какие размеры используются
for url in sorted(all_unsplash):
    print(f"  {url}")

# ===== 3. Просто заменим все unsplash на заглушку =====
# Сначала проверим какие фото teacher использует
teacher_urls = [u for u in all_unsplash if '1573496359142' in u or '1580894732444' in u]
print(f"\nСсылки преподавателя: {len(teacher_urls)}")

# Заменяем все unsplash ссылки на локальные
# Фото 1.jpg - для Екатерины
# Фото 2.jpg - для Дмитрия  
# Фото 3.jpg - для Артёма
# Фото 4.jpg - для Алины
# Фото 5.jpg - для Софии
# Фото 6.jpg - для Марии

replacements = {
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face': '/images/1.jpg',
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=80&h=80&fit=crop&crop=face': '/images/1.jpg',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face': '/images/2.jpg',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face': '/images/2.jpg',
    'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face': '/images/4.jpg',
    'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=80&h=80&fit=crop&crop=face': '/images/4.jpg',
    'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face': '/images/3.jpg',
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face': '/images/5.jpg',
    'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=150&h=150&fit=crop&crop=face': '/images/6.jpg',
}

for old, new in replacements.items():
    if old in html:
        html = html.replace(old, new)
        print(f"✅ Заменено: {old[:50]}... -> {new}")
    else:
        print(f"❌ Не найдено: {old[:50]}...")

# ===== 4. Обновляем версию =====
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=24.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=24.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("\n✅ HTML обновлён")

# ===== 5. Добавляем location для статики в nginx =====
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/default")
nginx_conf = stdout.read().decode()

# Добавляем location для /images/
if 'location /images/' not in nginx_conf:
    # Находим server_name и добавляем после него
    nginx_conf = nginx_conf.replace(
        "server_name _;",
        """server_name _;

    # Статические файлы
    location /images/ {
        alias /var/www/englishpro/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }"""
    )
    
    # Записываем
    stdin, stdout, stderr = ssh.exec_command("cat > /etc/nginx/sites-enabled/default << 'NGINX_EOF'\n" + nginx_conf + "\nNGINX_EOF")
    print(stdout.read().decode())
    print(stderr.read().decode())
    print("✅ Nginx config обновлён (добавлен location /images/)")
else:
    print("✅ location /images/ уже есть в nginx")

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n🎉 Готово! Фото должны отображаться")
