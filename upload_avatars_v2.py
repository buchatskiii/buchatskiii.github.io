import requests
import os
import paramiko

# Pinterest pin IDs - используем 474x размер (доступен всегда)
pins = [
    ("student_1.jpg", "https://i.pinimg.com/474x/12/50/ae/1250ae0e43c9a1282e821ab65dcd7070.jpg"),
    ("student_2.jpg", "https://i.pinimg.com/474x/ae/db/dc/aedbdcd6ae8be9ace03c89d61b7c0e30.jpg"),
    ("student_3.jpg", "https://i.pinimg.com/474x/b2/14/2e/b2142e3b6d73fe1f1cb30c295f3e31cb.jpg"),
    ("student_4.jpg", "https://i.pinimg.com/474x/ca/76/33/ca763381e207ea3ae332f6ea4f0ef248.jpg"),
    ("student_5.jpg", "https://i.pinimg.com/474x/9e/25/3a/9e253a129bc237169595d016ceb656dc.jpg"),
    ("student_6.jpg", "https://i.pinimg.com/474x/53/24/58/5324584dd4b5542f00929d2e69448b43.jpg"),
]

os.makedirs("avatars_final", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.pinterest.com/"
}

print("=== Скачиваем аватарки (474x) ===")
for filename, url in pins:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 5000:
            path = f"avatars_final/{filename}"
            with open(path, 'wb') as f:
                f.write(resp.content)
            print(f"✅ {filename} - {len(resp.content)//1024}KB")
        else:
            print(f"❌ {filename} - статус {resp.status_code}, размер {len(resp.content)}")
            # Пробуем 236x
            url236 = url.replace("/474x/", "/236x/")
            resp2 = requests.get(url236, headers=headers, timeout=15)
            if resp2.status_code == 200 and len(resp2.content) > 3000:
                path = f"avatars_final/{filename}"
                with open(path, 'wb') as f:
                    f.write(resp2.content)
                print(f"  ✅ {filename} (236x) - {len(resp2.content)//1024}KB")
    except Exception as e:
        print(f"❌ {filename} - ошибка: {e}")

print("\n=== Загружаем на сервер ===")
host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# Создаём папку для аватарок на сервере
try:
    sftp.mkdir("/var/www/englishpro/images/avatars")
except:
    pass

for filename, url in pins:
    local_path = f"avatars_final/{filename}"
    if os.path.exists(local_path):
        remote_path = f"/var/www/englishpro/images/avatars/{filename}"
        sftp.put(local_path, remote_path)
        print(f"✅ Загружен {filename}")

# ===== Обновляем HTML =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

import re

# Заменяем все unsplash ссылки на наши аватарки
# В результатах (6 штук) и отзывах (3 штуки) - всего 9
replacements = [
    # Результаты
    ("https://images.unsplash.com/photo-1494790108377-be9c29b29330", "/images/avatars/student_1.jpg"),
    ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d", "/images/avatars/student_2.jpg"),
    ("https://images.unsplash.com/photo-1438761681033-6461ffad8d80", "/images/avatars/student_3.jpg"),
    ("https://images.unsplash.com/photo-1500648767791-00dcc994a43e", "/images/avatars/student_4.jpg"),
    ("https://images.unsplash.com/photo-1544005313-94ddf0286df2", "/images/avatars/student_5.jpg"),
    ("https://images.unsplash.com/photo-1531746020798-e6953c6e8e04", "/images/avatars/student_6.jpg"),
]

for old, new in replacements:
    html = html.replace(old, new)

# Обновляем версию
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=10.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=10.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))

sftp.close()
ssh.close()
print("\n✅ HTML обновлён! Аватарки загружены на сервер.")
print("   Ссылки unsplash заменены на /images/avatars/student_X.jpg")
