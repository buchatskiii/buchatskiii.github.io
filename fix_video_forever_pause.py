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
old_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

new_video = '''<video id="aboutVideo" preload="auto" playsinline controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

if old_video in html:
    html = html.replace(old_video, new_video)
    print("✅ Video тег: убран autoplay и loop")

# 2. Скрипт: если пользователь нажал паузу - отключаем IntersectionObserver навсегда
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    var userPaused = false;
    var observer = null;
    
    video.volume = 0.33;
    if (isMobile) {
        video.muted = true;
    }
    
    // Если пользователь нажал паузу - отключаем observer навсегда
    video.addEventListener('pause', function() {
        userPaused = true;
        // Отключаем IntersectionObserver - видео больше никогда не запустится само
        if (observer) {
            observer.disconnect();
            observer = null;
        }
    });
    
    // Если пользователь нажал play - снова включаем observer
    video.addEventListener('play', function() {
        userPaused = false;
        // Включаем observer обратно
        if (!observer && 'IntersectionObserver' in window) {
            observer = new IntersectionObserver(function(entries) {
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
    });
    
    function playWithSound() {
        video.volume = 0.33;
        if (!isMobile) {
            video.muted = false;
        }
        var p = video.play();
        if (p && p['catch']) {
            p['catch'](function(){});
        }
    }
    
    function pauseVideo() {
        video.pause();
    }
    
    // Создаём observer
    if ('IntersectionObserver' in window) {
        observer = new IntersectionObserver(function(entries) {
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
    
    // На мобильных - клик включает звук
    if (isMobile) {
        video.addEventListener('click', function() {
            video.muted = false;
            video.volume = 0.33;
        });
        video.addEventListener('touchstart', function() {
            video.muted = false;
            video.volume = 0.33;
        });
    }
    
    console.log('Video: user pause = forever pause');
})();
</script>'''

html = re.sub(old_script_pattern, new_script, html, flags=re.DOTALL)
print("✅ Скрипт заменён: пауза пользователя = навсегда")

# Обновляем версию
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=40.0', html)
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=40.0', html)

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

print("🎉 Готово! Пауза пользователя = навсегда, пока сам не нажмёт Play")
