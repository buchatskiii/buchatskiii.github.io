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

# 1. Video тег: autoplay + muted (для автозапуска) + controls
old_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

new_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay muted controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

if old_video in html:
    html = html.replace(old_video, new_video)
    print("✅ Video тег: autoplay + muted + controls")
else:
    print("❌ Старый video тег не найден!")
    m = re.search(r'<video[^>]*>', html)
    if m:
        print(f"Текущий тег: {m.group()}")

# 2. Заменяем скрипт на правильный
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    video.volume = 0.33;
    
    // Включаем звук и запускаем
    function playWithSound() {
        video.muted = false;
        video.volume = 0.33;
        var p = video.play();
        if (p && p['catch']) {
            p['catch'](function(){});
        }
    }
    
    // Ставим на паузу
    function pauseVideo() {
        video.pause();
    }
    
    // IntersectionObserver - видео играет только когда видно
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
        var isVisible = rect.top < window.innerHeight - 100 && rect.bottom > 100;
        if (isVisible) {
            playWithSound();
        }
    });
    
    // При клике включаем звук
    document.addEventListener('click', function() {
        video.muted = false;
        video.volume = 0.33;
    });
    
    // При изменении громкости пользователем - не сбрасываем, но при старте ставим 0.33
    video.addEventListener('play', function() {
        video.volume = 0.33;
    });
    
    console.log('Video: play when visible, pause when hidden, volume 33%');
})();
</script>'''

html = re.sub(old_script_pattern, new_script, html, flags=re.DOTALL)
print("✅ Скрипт заменён: play при видимости, pause при скрытии")

# Обновляем версию
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=32.0', html)
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=32.0', html)

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

print("🎉 Готово! Видео: автозапуск со звуком 33% при появлении, пауза при уходе с экрана")
