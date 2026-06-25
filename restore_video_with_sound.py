import paramiko
import re
import random

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Заменяем изображение обратно на видео
old_block = '''<div class="about-image" style="position:relative;border-radius:20px;overflow:hidden;background:#1a1a2e;min-height:400px;">
    <img src="https://images.unsplash.com/photo-1571260899304-425eee4c7efc?w=800&h=500&fit=crop" 
         alt="О преподавателе" 
         style="width:100%;height:100%;min-height:400px;object-fit:cover;border-radius:20px;display:block;">
    <div style="position:absolute;top:0;left:0;right:0;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:rgba(0,0,0,0.3);border-radius:20px;">
        <a href="/videos/povelitel_vselennoy.mp4" target="_blank" 
           style="display:inline-flex;align-items:center;gap:12px;padding:16px 32px;background:#6c63ff;color:white;border-radius:50px;text-decoration:none;font-size:18px;font-weight:600;box-shadow:0 8px 30px rgba(108,99,255,0.4);">
            <span style="font-size:24px;">▶</span>
            Смотреть видео
        </a>
        <p style="color:rgba(255,255,255,0.8);margin-top:12px;font-size:14px;">Откроется в новой вкладке</p>
    </div>
</div>'''

new_block = '''<div class="about-image" id="aboutVideoWrapper">
    <div class="video-container">
        <video id="aboutVideo" preload="auto" playsinline controls
            style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">
            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
            Ваш браузер не поддерживает видео
        </video>
    </div>
</div>'''

if old_block in html:
    html = html.replace(old_block, new_block)
    print("✅ Видео восстановлено")
else:
    print("❌ Блок изображения не найден!")
    # Проверим, может уже есть видео
    if 'aboutVideo' in html:
        print("   aboutVideo уже есть в HTML")
    if '<video' in html:
        print("   video тег уже есть в HTML")

# Добавляем скрипт управления видео
# Сначала удаляем старый скрипт если есть
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
html = re.sub(old_script_pattern, '', html, flags=re.DOTALL)

# Добавляем новый скрипт перед закрывающим </body>
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    var userPaused = false;
    
    video.volume = 0.33;
    if (isMobile) {
        video.muted = true;
    }
    
    // Пользователь нажал паузу - запоминаем
    video.addEventListener('pause', function() {
        userPaused = true;
    });
    
    // Пользователь нажал play - сбрасываем
    video.addEventListener('play', function() {
        userPaused = false;
    });
    
    function tryPlay() {
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
    
    // IntersectionObserver для автозапуска при появлении
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    tryPlay();
                } else {
                    video.pause();
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
    
    console.log('Video: autoplay with sound, userPause flag');
})();
</script>'''

html = html.replace('</body>', new_script + '\n</body>')
print("✅ Скрипт управления видео добавлен")

# Уникальная версия
ver = str(random.randint(100, 999))
html = re.sub(r'script\.js\?v=[\d.]+', f'script.js?v={ver}', html)
html = re.sub(r'styles\.css\?v=[\d.]+', f'styles.css?v={ver}', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print(f"✅ HTML сохранён (v={ver})")

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("🎉 Готово! Видео восстановлено с автозапуском и звуком")
