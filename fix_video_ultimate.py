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

# Читаем HTML
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Полностью переписываем скрипт
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    var observer = null;
    
    video.volume = 0.33;
    if (isMobile) {
        video.muted = true;
    }
    
    // Если пользователь нажал паузу - отключаем observer НАВСЕГДА
    video.addEventListener('pause', function() {
        if (observer) {
            observer.disconnect();
            observer = null;
        }
    });
    
    // Если пользователь нажал play - включаем observer обратно
    video.addEventListener('play', function() {
        if (!observer && 'IntersectionObserver' in window) {
            observer = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        playWithSound();
                    } else {
                        video.pause();
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
    
    // Создаём observer
    if ('IntersectionObserver' in window) {
        observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    playWithSound();
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
    
    console.log('Video: ultimate version - pause disconnects observer forever');
})();
</script>'''

html = re.sub(old_script_pattern, new_script, html, flags=re.DOTALL)
print("✅ Скрипт заменён: ультимативная версия")

# Уникальная версия для сброса кеша
ver = str(random.randint(100, 999))
html = re.sub(r'script\.js\?v=[\d.]+', f'script.js?v={ver}', html)
html = re.sub(r'styles\.css\?v=[\d.]+', f'styles.css?v={ver}', html)

# Сохраняем
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

print("🎉 Готово! Ультимативная версия")
