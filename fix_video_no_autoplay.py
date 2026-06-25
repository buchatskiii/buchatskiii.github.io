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

# 1. Video тег: убираем autoplay и loop, оставляем только controls
old_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

new_video = '''<video id="aboutVideo" preload="auto" playsinline controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

if old_video in html:
    html = html.replace(old_video, new_video)
    print("✅ Video тег: убран autoplay и loop")
else:
    print("❌ Старый тег не найден, ищем текущий...")
    m = re.search(r'<video[^>]*>', html)
    if m:
        print(f"Текущий: {m.group()}")

# 2. Скрипт: полностью управляем через JS
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    var userPaused = false;
    var scriptPausing = false;
    var wasPlaying = false;
    
    video.volume = 0.33;
    if (isMobile) {
        video.muted = true;
    }
    
    // Пользователь нажал паузу
    video.addEventListener('pause', function() {
        if (!scriptPausing) {
            userPaused = true;
            wasPlaying = false;
        }
    });
    
    // Пользователь нажал play
    video.addEventListener('play', function() {
        userPaused = false;
        wasPlaying = true;
    });
    
    function playWithSound() {
        if (userPaused) return;
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
    
    console.log('Video: no autoplay attr, full JS control');
})();
</script>'''

html = re.sub(old_script_pattern, new_script, html, flags=re.DOTALL)
print("✅ Скрипт заменён: полный контроль через JS")

# Обновляем версию
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=39.0', html)
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=39.0', html)

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

print("🎉 Готово! Полный контроль видео через JS")
