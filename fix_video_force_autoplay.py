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
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;"
    defaultMuted="false">'''

new_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

if old_video in html:
    html = html.replace(old_video, new_video)
    print("✅ Video тег: убран muted, оставлены autoplay + controls")
else:
    print("❌ Старый video тег не найден!")
    m = re.search(r'<video[^>]*>', html)
    if m:
        print(f"Текущий тег: {m.group()}")

# 2. Заменяем скрипт на агрессивный
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    video.volume = 0.33;
    
    // Агрессивный автозапуск со звуком
    function forcePlay() {
        video.volume = 0.33;
        video.muted = false;
        var p = video.play();
        if (p && p['catch']) {
            p['catch'](function() {
                // Если заблокировали - пробуем снова через 100мс
                setTimeout(forcePlay, 100);
            });
        }
    }
    
    // Пробуем сразу
    forcePlay();
    
    // Пробуем при canplay
    video.addEventListener('canplay', forcePlay);
    video.addEventListener('loadedmetadata', forcePlay);
    video.addEventListener('loadeddata', forcePlay);
    
    // При появлении в зоне видимости
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    forcePlay();
                }
            });
        }, {threshold: 0.01});
        observer.observe(video);
    }
    
    // При скролле
    window.addEventListener('scroll', function() {
        var rect = video.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            forcePlay();
        }
    });
    
    // При клике
    document.addEventListener('click', forcePlay);
    document.addEventListener('touchstart', forcePlay);
    
    // Каждые 500мс проверяем и пробуем запустить
    setInterval(function() {
        if (video.paused) {
            forcePlay();
        }
        video.volume = 0.33;
    }, 500);
    
    console.log('Force autoplay with sound 33%');
})();
</script>'''

html = re.sub(old_script_pattern, new_script, html, flags=re.DOTALL)
print("✅ Скрипт заменён на агрессивный автозапуск")

# Обновляем версию
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=31.0', html)
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=31.0', html)

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

print("🎉 Готово! Видео будет принудительно запускаться со звуком 33% при появлении на экране")
