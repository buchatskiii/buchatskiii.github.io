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

# Удаляем старый скрипт
old_script_pattern = r'<script>\n\(function\(\).*?</script>'
html = re.sub(old_script_pattern, '', html, flags=re.DOTALL)

# Добавляем новый скрипт с правильной логикой
new_script = '''<script>
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    var userPaused = false;  // true = пользователь нажал паузу, НАВСЕГДА
    
    video.volume = 0.33;
    if (isMobile) {
        video.muted = true;
    }
    
    // Пользователь нажал паузу - запоминаем НАВСЕГДА
    video.addEventListener('pause', function() {
        userPaused = true;
    });
    
    // Пользователь нажал play - НЕ сбрасываем userPaused!
    // Просто играем видео, автозапуск больше не вернётся
    
    function tryPlay() {
        if (userPaused) return;  // НИКОГДА не запускаем, если пользователь нажал паузу
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
    
    console.log('Video: userPause = FOREVER, play does NOT reset');
})();
</script>'''

html = html.replace('</body>', new_script + '\n</body>')
print("✅ Скрипт обновлён: userPause НАВСЕГДА, Play не сбрасывает")

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

print("🎉 Готово! Финальная логика: пауза = навсегда")
