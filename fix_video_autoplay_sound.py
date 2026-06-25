import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# Читаем текущий HTML
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Находим секцию с видео
import re

# Ищем video тег
video_match = re.search(r'<video[^>]*>', html)
if video_match:
    print(f"Найден video тег: {video_match.group()}")
else:
    print("Video тег не найден!")

# Ищем секцию about video
about_video_match = re.search(r'about-video[^>]*>.*?</section>', html, re.DOTALL)
if about_video_match:
    print(f"\nНайдена секция about-video")
else:
    print("\nСекция about-video не найдена")

# Ищем весь блок about
about_match = re.search(r'<section class="about section"[^>]*>.*?</section>', html, re.DOTALL)
if about_match:
    about_section = about_match.group()
    print(f"\nСекция about найдена, длина: {len(about_section)}")
    
    # Проверяем есть ли видео внутри
    if 'video' in about_section:
        print("Видео есть внутри about секции")
    else:
        print("Видео НЕТ внутри about секции")
else:
    print("Секция about не найдена")

# Ищем все упоминания video
video_refs = re.findall(r'[^.]*video[^.]*\.', html, re.IGNORECASE)
print(f"\nВсе упоминания video ({len(video_refs)}):")
for ref in video_refs:
    print(f"  ...{ref[:100]}...")

sftp.close()
ssh.close()
