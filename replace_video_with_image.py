import paramiko
import re
import random

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Заменяем весь блок с видео на статичное изображение с кнопкой
old_video_block = '''<div class="about-video">
    <video id="aboutVideo" preload="auto" playsinline controls
        style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">
        <source src="https://beklox.ru/video/about.mp4" type="video/mp4">
        Ваш браузер не поддерживает видео.
    </video>
</div>'''

new_video_block = '''<div class="about-video" style="position:relative;width:100%;height:100%;border-radius:20px;overflow:hidden;background:#1a1a2e;">
    <img src="https://images.unsplash.com/photo-1571260899304-425eee4c7efc?w=800&h=500&fit=crop" 
         alt="О преподавателе" 
         style="width:100%;height:100%;object-fit:cover;border-radius:20px;display:block;">
    <div style="position:absolute;top:0;left:0;right:0;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);border-radius:20px;">
        <a href="https://beklox.ru/video/about.mp4" target="_blank" 
           style="display:inline-flex;align-items:center;gap:12px;padding:16px 32px;background:#6c63ff;color:white;border-radius:50px;text-decoration:none;font-size:18px;font-weight:600;transition:all 0.3s;box-shadow:0 8px 30px rgba(108,99,255,0.4);"
           onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <span style="font-size:24px;">▶</span>
            Смотреть видео обо мне
        </a>
        <p style="color:rgba(255,255,255,0.8);margin-top:12px;font-size:14px;">Откроется в новой вкладке</p>
    </div>
</div>'''

if old_video_block in html:
    html = html.replace(old_video_block, new_video_block)
    print("✅ Видео заменено на изображение с кнопкой")
else:
    print("❌ Блок видео не найден!")
    # Попробуем найти частично
    if 'about-video' in html:
        print("   about-video div найден")
    if 'aboutVideo' in html:
        print("   aboutVideo id найден")

# Убираем весь скрипт управления видео
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
html = re.sub(old_script_pattern, '', html, flags=re.DOTALL)
print("✅ Скрипт управления видео удалён")

# Убираем autoplay и loop из всех video тегов
html = html.replace('autoplay ', '')
html = html.replace('autoplay"', '"')
html = html.replace("autoplay'", "'")
html = html.replace('loop ', '')
html = html.replace('loop"', '"')
html = html.replace("loop'", "'")

# Уникальная версия
ver = str(random.randint(100, 999))
html = re.sub(r'script\.js\?v=[\d.]+', f'script.js?v={ver}', html)
html = re.sub(r'styles\.css\?v=[\d.]+', f'styles.css?v={ver}', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print(f"✅ HTML сохранён (v={ver})")

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("🎉 Готово! Видео заменено на изображение с кнопкой")
