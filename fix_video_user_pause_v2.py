import paramiko
import re

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# Читаем HTML
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# 1. Video тег
old_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay muted controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

new_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

if old_video in html:
    html = html.replace(old_video, new_video)
    print("✅ Video тег: убран muted")

# 2. Скрипт с правильным различением ручной и автоматической паузы
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    video.volume = 0.33;
    var userPaused = false;
    var scriptPausing = false;
    
    // Если пользователь сам нажал паузу - запоминаем
    video.addEventListener('pause', function() {
        if (!scriptPausing) {
            userPaused = true;
        }
    });
    
    // Если пользователь сам нажал play - сбрасываем флаг
    video.addEventListener('play', function() {
        userPaused = false;
    });
    
    // Запуск со звуком (только если не было ручной паузы)
    function playWithSound() {
        if (userPaused) return;
        video.volume = 0.33;
        var p = video.play();
        if (p && p['catch']) {
            p['catch'](function(){});
        }
    }
    
    // Остановка (с флагом, чтобы не считать это ручной паузой)
    function pauseVideo() {
        scriptPausing = true;
        video.pause();
        scriptPausing = false;
    }
    
    // IntersectionObserver
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    playWithSound();
                } else {
                    pauseVideo();
                }
            });
        }, {threshold: 0.3});
        observer.observe(video);
    }
    
    // При скролле
    window.addEventListener('scroll', function() {
        var rect = video.getBoundingClientRect();
        var isVisible = rect.top < window.innerHeight - 50 && rect.bottom > 50;
        if (isVisible) {
            playWithSound();
        }
    });
    
    console.log('Video: autoplay, respects user pause (fixed)');
})();
</script>'''

html = re.sub(old_script_pattern, new_script, html, flags=re.DOTALL)
print("✅ Скрипт заменён: правильное различие ручной и автоматической паузы")

# Обновляем версию
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=36.0', html)
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=36.0', html)

# Сохраняем
with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML сохранён")

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("🎉 Готово! Видео: автозапуск, уважает ручную паузу (исправлено)")
