import requests
import os
import paramiko

# Pinterest pin IDs и большие версии изображений
# Меняем 236x на originals
pins_big = [
    ("student_1.jpg", "https://i.pinimg.com/originals/12/50/ae/1250ae0e43c9a1282e821ab65dcd7070.jpg"),
    ("student_2.jpg", "https://i.pinimg.com/originals/ae/db/dc/aedbdcd6ae8be9ace03c89d61b7c0e30.jpg"),
    ("student_3.jpg", "https://i.pinimg.com/originals/b2/14/2e/b2142e3b6d73fe1f1cb30c295f3e31cb.jpg"),
    ("student_4.jpg", "https://i.pinimg.com/originals/ca/76/33/ca763381e207ea3ae332f6ea4f0ef248.jpg"),
    ("student_5.jpg", "https://i.pinimg.com/originals/9e/25/3a/9e253a129bc237169595d016ceb656dc.jpg"),
    ("student_6.jpg", "https://i.pinimg.com/originals/53/24/58/5324584dd4b5542f00929d2e69448b43.jpg"),
]

os.makedirs("avatars_big", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("=== Скачиваем большие версии аватарок ===")
for filename, url in pins_big:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 5000:
            path = f"avatars_big/{filename}"
            with open(path, 'wb') as f:
                f.write(resp.content)
            print(f"✅ {filename} - {len(resp.content)//1024}KB")
        else:
            print(f"❌ {filename} - статус {resp.status_code}, размер {len(resp.content)}")
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

for filename, url in pins_big:
    local_path = f"avatars_big/{filename}"
    if os.path.exists(local_path):
        remote_path = f"/var/www/englishpro/images/avatars/{filename}"
        sftp.put(local_path, remote_path)
        print(f"✅ Загружен {filename}")

sftp.close()

# ===== Обновляем HTML =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Заменяем ссылки на аватарки учеников в результатах
# Сейчас там unsplash ссылки, меняем на наши
import re

# Назначаем аватарки ученикам (по порядку в results-grid)
# 1. Екатерина В. -> student_1
# 2. Дмитрий К. -> student_2
# 3. Алина М. -> student_3
# 4. Артём С. -> student_4
# 5. София Л. -> student_5
# 6. Мария Д. -> student_6

# В отзывах:
# 1. Екатерина В. -> student_1
# 2. Дмитрий К. -> student_2
# 3. Алина М. -> student_3

# Счётчики для замены
result_count = 0
testimonial_count = 0

def replace_result_avatar(match):
    global result_count
    result_count += 1
    return f'<img src="/images/avatars/student_{result_count}.jpg" alt="Ученик">'

def replace_testimonial_avatar(match):
    global testimonial_count
    testimonial_count += 1
    return f'<img src="/images/avatars/student_{testimonial_count}.jpg" alt="Ученик">'

# Заменяем в results-grid (первые 6 unsplash ссылок)
# Сначала в результатах
html = re.sub(
    r'<img src="https://images\.unsplash\.com/[^"]*"[^>]*alt="[^"]*"[^>]*>',
    replace_result_avatar,
    html,
    count=6
)

# Потом в отзывах (следующие 3)
html = re.sub(
    r'<img src="https://images\.unsplash\.com/[^"]*"[^>]*alt="[^"]*"[^>]*>',
    replace_testimonial_avatar,
    html,
    count=3
)

# Обновляем версию
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=9.1', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=9.1', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))

ssh.close()
print(f"\n✅ HTML обновлён! Заменено {result_count} аватарок в результатах и {testimonial_count} в отзывах")
