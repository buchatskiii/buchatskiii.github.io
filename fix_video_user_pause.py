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

# 1. Video тег: убираем muted, оставляем autoplay + controls
old_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay muted controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

new_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

if old_video in html:
    html = html.replace(old_video, new_video)
    print("✅ Video тег: убран muted")
else:
    m = re.search(r'<video[^>]*>', html)
    if m:
        print(f"Текущий тег: {m.group()}")

# 2. Скрипт с флагом userPaused
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    video.volume = 0.33;
    var userPaused = false;
    
    // Если пользователь сам нажал паузу - запоминаем
    video.addEventListener('pause', function() {
        userPaused = true;
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
    
    // Остановка
    function pauseVideo() {
        video.pause();
    }
    
    // IntersectionObserver - видео играет только когда видно на экране
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
    
    // При скролле проверяем видимость
    window.addEventListener('scroll', function() {
        var rect = video.getBoundingClientRect();
        var isVisible = rect.top < window.innerHeight - 50 && rect.bottom > 50;
        if (isVisible) {
            playWithSound();
        }
    });
    
    console.log('Video: autoplay with sound, respects user pause');
})();
</script>'''

html = re.sub(old_script_pattern, new_script, html, flags=re.DOTALL)
print("✅ Скрипт заменён: уважает ручную паузу пользователя")

# Обновляем версию
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=35.0', html)
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=35.0', html)

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

print("🎉 Готово! Видео уважает ручную паузу пользователя")
