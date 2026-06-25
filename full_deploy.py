import requests
import os
import paramiko

# ===== 1. Скачиваем аватарки =====
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
    "Referer": "https://www.pinterest.com/"
}

print("=== Скачиваем аватарки ===")
for filename, url in pins:
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 200 and len(resp.content) > 5000:
        with open(f"avatars_final/{filename}", 'wb') as f:
            f.write(resp.content)
        print(f"✅ {filename} - {len(resp.content)//1024}KB")
    else:
        print(f"❌ {filename} - статус {resp.status_code}")

# ===== 2. Подключаемся к серверу =====
host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# ===== 3. Загружаем видео =====
local_video = r"C:\Users\dlyav\Desktop\english-tutor\videos\повелитель вселенной.MP4"
try:
    sftp.mkdir("/var/www/englishpro/videos")
except:
    pass
print("\n=== Загружаем видео ===")
sftp.put(local_video, "/var/www/englishpro/videos/povelitel_vselennoy.mp4")
print("✅ Видео загружено!")

# ===== 4. Загружаем аватарки =====
try:
    sftp.mkdir("/var/www/englishpro/images/avatars")
except:
    pass
print("\n=== Загружаем аватарки ===")
for f in os.listdir("avatars_final"):
    if f.endswith(".jpg"):
        sftp.put(f"avatars_final/{f}", f"/var/www/englishpro/images/avatars/{f}")
        print(f"✅ {f}")

# ===== 5. Правим HTML =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

import re

# Меняем unsplash на локальные
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

html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=12.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=12.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("\n✅ HTML обновлён")

# ===== 6. Правим JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

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

start = js.find('// ===== Video in About section')
if start >= 0:
    end = js.find('// =====', start + 10)
    if end < 0:
        end = len(js)
    js = js[:start] + new_video_js + js[end:]
else:
    js += "\n" + new_video_js

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))
print("✅ JS обновлён")

sftp.close()
ssh.close()

# ===== 7. Перезапускаем nginx =====
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n🎉 ВСЁ ГОТОВО!")
print("   - Видео загружено и настроено (со звуком при скролле)")
print("   - 6 аватарок учеников загружены")
print("   - HTML и JS обновлены")
print("   - Nginx перезапущен")
