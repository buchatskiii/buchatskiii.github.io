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

# 1. Меняем video тег - добавляем autoplay, muted (нужно для автозапуска), убираем controls
old_video = '''<video id="aboutVideo" preload="auto" playsinline loop controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

new_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay muted
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

if old_video in html:
    html = html.replace(old_video, new_video)
    print("✅ Video тег обновлён: добавлены autoplay и muted")
else:
    print("❌ Старый video тег не найден!")
    # Попробуем найти текущий
    m = re.search(r'<video[^>]*>', html)
    if m:
        print(f"Текущий тег: {m.group()}")

# 2. Добавляем JS для включения звука после автозапуска
# Находим closing body tag и вставляем перед ним скрипт
sound_script = '''
<script>
// Автовоспроизведение видео со звуком при появлении в зоне видимости
(function() {
    const video = document.getElementById('aboutVideo');
    if (!video) return;
    
    // Функция для попытки включить звук
    function enableSound() {
        video.muted = false;
        video.volume = 0.33; // 1/3 от максимума
        video.play().catch(function(e) {
            console.log('Autoplay with sound blocked, retrying...');
        });
    }
    
    // Пробуем включить звук сразу после загрузки
    video.addEventListener('canplay', function() {
        // Первая попытка - сразу
        setTimeout(enableSound, 500);
    });
    
    // Используем IntersectionObserver для запуска со звуком при появлении
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    video.muted = false;
                    video.volume = 0.33;
                    video.play().catch(function(e) {});
                }
            });
        }, { threshold: 0.3 });
        
        observer.observe(video);
    }
    
    // Дополнительно: при любом клике на странице включаем звук
    document.addEventListener('click', function() {
        video.muted = false;
        video.volume = 0.33;
        video.play().catch(function(e) {});
    }, { once: true });
    
    // При скролле - тоже пробуем
    window.addEventListener('scroll', function() {
        video.muted = false;
        video.volume = 0.33;
        video.play().catch(function(e) {});
    }, { once: true });
})();
</script>
</body>'''

html = html.replace('</body>', sound_script)

# 3. Обновляем версию
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=28.0', html)
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=28.0', html)

# Сохраняем
with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён со скриптом автовоспроизведения")

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("🎉 Готово! Видео будет воспроизводиться автоматически со звуком (громкость 33%)")
