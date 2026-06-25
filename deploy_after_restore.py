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

# ===== 1. Загружаем видео =====
local_video = r"C:\Users\dlyav\Desktop\english-tutor\videos\повелитель вселенной.MP4"
remote_video = "/var/www/englishpro/videos/povelitel_vselennoy.mp4"

# Создаём папку videos
try:
    sftp.mkdir("/var/www/englishpro/videos")
except:
    pass

print("Загружаю видео...")
sftp.put(local_video, remote_video)
print("✅ Видео загружено!")

# ===== 2. Загружаем аватарки =====
try:
    sftp.mkdir("/var/www/englishpro/images/avatars")
except:
    pass

avatars_dir = "C:/Users/dlyav/Desktop/english-tutor/avatars_final"
if os.path.exists(avatars_dir):
    for f in os.listdir(avatars_dir):
        if f.endswith(".jpg"):
            local = os.path.join(avatars_dir, f)
            remote = f"/var/www/englishpro/images/avatars/{f}"
            sftp.put(local, remote)
            print(f"✅ Аватарка {f} загружена")

# ===== 3. Читаем HTML и правим =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

import re

# Меняем ссылки unsplash на локальные аватарки
replacements = [
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
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=11.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=11.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён — аватарки подключены")

# ===== 4. Читаем JS и правим видео =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Новый блок для видео
new_video_js = """// ===== Video in About section =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    
    if (!video || !videoWrapper) return;
    
    function isElementPartiallyVisible(el) {
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < windowHeight - 50 && rect.bottom > 50;
    }
    
    let wasInView = false;
    let userPaused = false;
    
    window.addEventListener('scroll', function() {
        const isInView = isElementPartiallyVisible(videoWrapper);
        
        if (isInView && !wasInView && !userPaused) {
            video.muted = false;
            video.volume = 1.0;
            video.play().catch(function(){});
        } else if (!isInView && wasInView) {
            if (!video.paused) {
                video.pause();
            }
        }
        
        wasInView = isInView;
    }, { passive: true });
    
    video.addEventListener('pause', function() {
        if (isElementPartiallyVisible(videoWrapper)) {
            userPaused = true;
        } else {
            userPaused = false;
        }
    });
    
    video.addEventListener('play', function() {
        userPaused = false;
    });
    
    document.querySelectorAll('a[href="#about"]').forEach(function(link) {
        link.addEventListener('click', function() {
            setTimeout(function() {
                if (isElementPartiallyVisible(videoWrapper) && video.paused) {
                    video.muted = false;
                    video.volume = 1.0;
                    video.play().catch(function(){});
                    userPaused = false;
                }
            }, 800);
        });
    });
    
    video.addEventListener('ended', function() {
        video.currentTime = 0;
        userPaused = false;
    });
});"""

# Заменяем старый блок
start = js.find('// ===== Video in About section')
if start >= 0:
    end = js.find('// =====', start + 10)
    if end < 0:
        end = len(js)
    js = js[:start] + new_video_js + js[end:]
    print("✅ JS видео блок обновлён")
else:
    js += "\n" + new_video_js
    print("✅ JS видео блок добавлен")

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))

sftp.close()
ssh.close()

# ===== 5. Перезапускаем nginx =====
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n✅ Всё готово!")
print("   - Видео загружено")
print("   - Аватарки загружены")
print("   - HTML обновлён")
print("   - JS обновлён (видео со звуком при скролле)")
