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

# 1. Меняем video тег - добавляем controls обратно, autoplay, muted
old_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay muted
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

new_video = '''<video id="aboutVideo" preload="auto" playsinline loop autoplay muted controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">'''

if old_video in html:
    html = html.replace(old_video, new_video)
    print("✅ Video тег обновлён: добавлены controls")
else:
    print("❌ Старый video тег не найден!")
    m = re.search(r'<video[^>]*>', html)
    if m:
        print(f"Текущий тег: {m.group()}")

# 2. Заменяем скрипт на более надёжный
old_script = '''<script>
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
</script>'''

new_script = '''<script>
// Автовоспроизведение видео со звуком + controls для управления
(function() {
    const video = document.getElementById('aboutVideo');
    if (!video) return;
    
    // Устанавливаем громкость 33%
    video.volume = 0.33;
    
    // Функция включения звука
    function enableSound() {
        if (!video.muted) return;
        video.muted = false;
        video.volume = 0.33;
        video.play().catch(function(e) {
            console.log('Autoplay blocked:', e.message);
        });
    }
    
    // Пробуем включить звук после загрузки метаданных
    video.addEventListener('loadedmetadata', function() {
        setTimeout(enableSound, 300);
    });
    
    // Пробуем при canplay
    video.addEventListener('canplay', function() {
        setTimeout(enableSound, 500);
    });
    
    // При первом взаимодействии пользователя с любой частью страницы
    function onUserInteraction() {
        enableSound();
        document.removeEventListener('click', onUserInteraction);
        document.removeEventListener('touchstart', onUserInteraction);
        document.removeEventListener('scroll', onUserInteraction);
        window.removeEventListener('scroll', onUserInteraction);
    }
    
    document.addEventListener('click', onUserInteraction);
    document.addEventListener('touchstart', onUserInteraction);
    document.addEventListener('scroll', onUserInteraction);
    window.addEventListener('scroll', onUserInteraction);
    
    // IntersectionObserver - при появлении в зоне видимости
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    video.play().catch(function(e) {});
                    enableSound();
                }
            });
        }, { threshold: 0.2 });
        observer.observe(video);
    }
    
    console.log('Video autoplay with sound initialized (volume: 33%)');
})();
</script>'''

if old_script in html:
    html = html.replace(old_script, new_script)
    print("✅ Скрипт обновлён")
else:
    print("❌ Старый скрипт не найден!")
    # Проверим есть ли вообще какой-то скрипт
    scripts = re.findall(r'<script>.*?</script>', html, re.DOTALL)
    print(f"Найдено скриптов: {len(scripts)}")
    for i, s in enumerate(scripts):
        print(f"Скрипт {i}: {s[:100]}...")

# Обновляем версию
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=29.0', html)
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=29.0', html)

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

print("🎉 Готово! Видео с controls, автовоспроизведением и звуком 33%")
