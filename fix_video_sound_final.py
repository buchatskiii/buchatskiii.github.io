import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

# ===== 1. Читаем HTML =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Оставляем muted в HTML для автозапуска
# (браузеры требуют muted для autoplay)
# Но JS будет убирать muted при скролле

import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=9.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=9.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён — версия 9.0")

# ===== 2. Читаем JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Полностью заменяем блок video
new_js_block = """// ===== Video in About section =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    
    if (!video || !videoWrapper) return;
    
    // Функция проверки видимости
    function isElementPartiallyVisible(el) {
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < windowHeight - 50 && rect.bottom > 50;
    }
    
    let wasInView = false;
    let userPaused = false;
    
    // При скролле
    window.addEventListener('scroll', function() {
        const isInView = isElementPartiallyVisible(videoWrapper);
        
        if (isInView && !wasInView && !userPaused) {
            // Убираем muted и запускаем СО ЗВУКОМ
            video.muted = false;
            video.volume = 1.0;
            video.play().catch(function(){});
        } else if (!isInView && wasInView) {
            if (!video.paused) {
                video.pause();
            }
        }
        
        wasInView = isInView;
    }, { passive: true });
    
    // Если пользователь сам поставил паузу - не трогаем
    video.addEventListener('pause', function() {
        if (isElementPartiallyVisible(videoWrapper)) {
            userPaused = true;
        } else {
            userPaused = false;
        }
    });
    
    video.addEventListener('play', function() {
        userPaused = false;
    });
    
    // При клике по ссылке "Обо мне" в меню
    document.querySelectorAll('a[href="#about"]').forEach(function(link) {
        link.addEventListener('click', function() {
            setTimeout(function() {
                if (isElementPartiallyVisible(videoWrapper) && video.paused) {
                    video.muted = false;
                    video.volume = 1.0;
                    video.play().catch(function(){});
                    userPaused = false;
                }
            }, 800);
        });
    });
    
    video.addEventListener('ended', function() {
        video.currentTime = 0;
        userPaused = false;
    });
});"""

if 'aboutVideo' in js:
    # Находим старый блок и заменяем
    start = js.find('// ===== Video in About section')
    end = js.find('// =====', start + 10)
    if end < 0:
        end = len(js)
    js = js[:start] + new_js_block + js[end:]
    print("✅ JS обновлён")
else:
    js += "\n" + new_js_block
    print("✅ JS добавлен")

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))

sftp.close()
ssh.close()
print("\n✅ Готово!")
print("   - muted остаётся в HTML для автозапуска")
print("   - при скролле до блока 'Обо мне': muted=false, volume=1.0, play()")
print("   - видео запускается СО ЗВУКОМ!")
