import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# ===== 1. Читаем HTML - проверяем video тег =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

idx = html.find('aboutVideo')
if idx >= 0:
    print("=== Video тег ===")
    print(html[idx-100:idx+400])

# ===== 2. Переписываем JS целиком =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Находим начало видео-блока
start = js.find('// ===== Video')
if start >= 0:
    # Удаляем всё от видео-блока до конца
    js = js[:start]
    print("✅ Старый видео-блок удалён")

# Добавляем новый JS в самый конец
new_video_js = """
// ===== VIDEO: play when visible, pause when hidden =====
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) {
        console.log('Video element not found');
        return;
    }
    console.log('Video element found');
    
    function isVisible(el) {
        var rect = el.getBoundingClientRect();
        var wh = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < wh - 50 && rect.bottom > 50;
    }
    
    var soundReady = false;
    
    function handleVisibility() {
        var visible = isVisible(video);
        
        if (visible) {
            if (video.paused) {
                if (!soundReady) {
                    video.muted = true;
                    video.volume = 1.0;
                    video.play().then(function() {
                        setTimeout(function() {
                            video.muted = false;
                            soundReady = true;
                        }, 100);
                    }).catch(function(e) {
                        console.log('First play failed:', e);
                    });
                } else {
                    video.muted = false;
                    video.volume = 1.0;
                    video.play().catch(function(e) {
                        console.log('Replay failed:', e);
                    });
                }
            }
        } else {
            if (!video.paused) {
                video.pause();
            }
        }
    }
    
    // Проверяем сразу
    setTimeout(handleVisibility, 100);
    setTimeout(handleVisibility, 500);
    setTimeout(handleVisibility, 1000);
    
    // При скролле
    window.addEventListener('scroll', handleVisibility, { passive: true });
    
    // При изменении размера окна
    window.addEventListener('resize', handleVisibility, { passive: true });
})();
"""

js += new_video_js

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))
print("✅ JS полностью переписан")

# ===== 3. Обновляем HTML =====
import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=21.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=21.0', html)

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

print("\n🎉 Готово! Видео будет запускаться при появлении на экране")
