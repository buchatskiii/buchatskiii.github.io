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

# Находим начало видео-блока
start = js.find('// ===== VIDEO')
if start >= 0:
    js = js[:start]
    print("✅ Старый видео-блок удалён")

# Новый JS - максимально агрессивный
new_video_js = """
// ===== VIDEO: play with sound immediately =====
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    // Громкость 50%
    video.volume = 0.5;
    
    function isVisible(el) {
        var rect = el.getBoundingClientRect();
        var wh = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < wh - 50 && rect.bottom > 50;
    }
    
    function tryPlay() {
        if (video.paused) {
            video.muted = false;
            video.volume = 0.5;
            video.play().catch(function(){});
        }
    }
    
    function tryPause() {
        if (!video.paused) {
            video.pause();
        }
    }
    
    function handleVisibility() {
        if (isVisible(video)) {
            tryPlay();
        } else {
            tryPause();
        }
    }
    
    // Проверяем много раз при загрузке
    var checks = [0, 100, 300, 500, 800, 1000, 1500, 2000];
    for (var i = 0; i < checks.length; i++) {
        (function(delay) {
            setTimeout(handleVisibility, delay);
        })(checks[i]);
    }
    
    // При скролле
    window.addEventListener('scroll', handleVisibility, { passive: true });
    window.addEventListener('resize', handleVisibility, { passive: true });
})();
"""

js += new_video_js

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))
print("✅ JS обновлён")

# ===== 2. Обновляем HTML =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=22.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=22.0', html)

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

print("\n🎉 Готово! Видео со звуком (50%) сразу при появлении на экране")
