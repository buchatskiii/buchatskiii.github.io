import paramiko
import os

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# Создаём папку для фото на сервере
try:
    sftp.stat("/var/www/englishpro/images")
except:
    sftp.mkdir("/var/www/englishpro/images")

# Загружаем фото 1-6 (без teacher.jpg)
local_dir = r"C:\Users\dlyav\Desktop\english-tutor\images"
for i in range(1, 7):
    local_file = os.path.join(local_dir, f"{i}.jpg")
    remote_file = f"/var/www/englishpro/images/{i}.jpg"
    sftp.put(local_file, remote_file)
    print(f"✅ Загружено {i}.jpg")

# ===== Читаем HTML =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Заменяем ссылки на фото учеников в разделе "Результаты"
# Екатерина В. (девочка) - 1.jpg
old = 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face'
new = '/images/1.jpg'
html = html.replace(old, new)

# Дмитрий К. (мальчик) - 2.jpg
old = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face'
new = '/images/2.jpg'
html = html.replace(old, new)

# Алина М. (девочка) - 4.jpg
old = 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face'
new = '/images/4.jpg'
html = html.replace(old, new)

# Артём С. (мальчик) - 3.jpg
old = 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face'
new = '/images/3.jpg'
html = html.replace(old, new)

# София Л. (девочка) - 5.jpg
old = 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face'
new = '/images/5.jpg'
html = html.replace(old, new)

# Мария Д. (девочка) - 6.jpg
old = 'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=150&h=150&fit=crop&crop=face'
new = '/images/6.jpg'
html = html.replace(old, new)

# Теперь заменяем фото в отзывах (те же ученики)
# Екатерина В. в отзывах
old = 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=80&h=80&fit=crop&crop=face'
new = '/images/1.jpg'
html = html.replace(old, new)

# Дмитрий К. в отзывах
old = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop&crop=face'
new = '/images/2.jpg'
html = html.replace(old, new)

# Алина М. в отзывах
old = 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=80&h=80&fit=crop&crop=face'
new = '/images/4.jpg'
html = html.replace(old, new)

# Обновляем версию
import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=23.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=23.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён с локальными фото")

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n🎉 Готово! Фото учеников загружены на сервер")
