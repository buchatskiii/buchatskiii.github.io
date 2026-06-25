import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# ===== 1. Читаем JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Максимально простой JS
new_video_js = """// ===== Video autoplay with sound on scroll =====
document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('aboutVideo');
    if (!video) return;
    
    function isVisible(el) {
        const rect = el.getBoundingClientRect();
        const wh = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < wh - 50 && rect.bottom > 50;
    }
    
    function tryPlay() {
        if (video.paused) {
            video.muted = true;
            video.volume = 1.0;
            video.play().then(function() {
                setTimeout(function() {
                    video.muted = false;
                }, 50);
            }).catch(function(){});
        }
    }
    
    // Проверяем при скролле
    window.addEventListener('scroll', function() {
        if (isVisible(video)) {
            tryPlay();
        }
    }, { passive: true });
    
    // Проверяем сразу
    setTimeout(function() {
        if (isVisible(video)) {
            tryPlay();
        }
    }, 300);
});"""

# Заменяем старый блок
start = js.find('// ===== Video')
if start >= 0:
    end = js.find('// =====', start + 10)
    if end < 0:
        end = len(js)
    js = js[:start] + new_video_js + js[end:]
    print("✅ JS заменён")
else:
    js += "\n" + new_video_js
    print("✅ JS добавлен")

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))

# ===== 2. Обновляем HTML =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Убираем autoplay из HTML - пусть JS управляет
html = html.replace('autoplay ', '')
html = html.replace(' autoplay>', '>')

import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=19.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=19.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён")

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n🎉 Готово! Видео запускается сразу при появлении на экране")
