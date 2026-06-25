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

# 1. Правильный video тег
old_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay muted controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

new_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay muted controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;"
    defaultMuted="false">'''

if old_video in html:
    html = html.replace(old_video, new_video)
    print("✅ Video тег обновлён")
else:
    print("❌ Старый video тег не найден!")
    m = re.search(r'<video[^>]*>', html)
    if m:
        print(f"Текущий тег: {m.group()}")

# 2. Заменяем весь скрипт на простой и надёжный
old_script_pattern = r'<script>\n// Автовоспроизведение видео.*?</script>'
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    // Принудительно ставим громкость 0.33 при каждой возможности
    function setVolume() {
        video.volume = 0.33;
    }
    
    // Ставим сразу
    setVolume();
    
    // При загрузке метаданных
    video.addEventListener('loadedmetadata', setVolume);
    video.addEventListener('loadeddata', setVolume);
    video.addEventListener('canplay', function() {
        setVolume();
        // Пробуем включить звук
        video.muted = false;
        video.play()['catch'](function(){});
    });
    
    // При изменении громкости пользователем - возвращаем 0.33
    video.addEventListener('volumechange', function() {
        if (video.volume > 0.34 || video.volume < 0.32) {
            video.volume = 0.33;
        }
    });
    
    // При первом клике/скролле включаем звук
    function enableSound() {
        video.muted = false;
        video.volume = 0.33;
        video.play()['catch'](function(){});
    }
    
    document.addEventListener('click', enableSound, {once: true});
    document.addEventListener('scroll', enableSound, {once: true});
    document.addEventListener('touchstart', enableSound, {once: true});
    
    // IntersectionObserver
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    video.play()['catch'](function(){});
                    video.muted = false;
                    video.volume = 0.33;
                }
            });
        }, {threshold: 0.2});
        observer.observe(video);
    }
    
    console.log('Video: autoplay + volume 0.33');
})();
</script>'''

html = re.sub(old_script_pattern, new_script, html, flags=re.DOTALL)
print("✅ Скрипт обновлён")

# Обновляем версию
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=30.0', html)
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=30.0', html)

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

print("🎉 Готово! Видео: autoplay + controls + volume 0.33 (1/3)")
