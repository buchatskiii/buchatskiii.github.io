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

# Возвращаем muted для автозапуска
html = html.replace(
    'autoplay playsinline preload="auto" controls',
    'autoplay muted playsinline preload="auto" controls'
)

# Обновляем версию
import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=8.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=8.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён — muted возвращён для автозапуска")

# ===== 2. Читаем JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Новый JS — максимально агрессивный подход
new_js_block = """// ===== Video in About section =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    
    if (!video || !videoWrapper) return;
    
    // Сразу убираем muted и запускаем со звуком
    video.muted = false;
    video.volume = 1.0;
    
    // Пробуем запустить сразу
    function forcePlay() {
        video.muted = false;
        video.volume = 1.0;
        var p = video.play();
        if (p !== undefined) {
            p.catch(function() {
                // Если не вышло - пробуем снова через 100мс
                setTimeout(function() {
                    video.muted = false;
                    video.volume = 1.0;
                    video.play().catch(function() {
                        // Ещё одна попытка через 500мс
                        setTimeout(function() {
                            video.muted = false;
                            video.volume = 1.0;
                            video.play().catch(function() {});
                        }, 500);
                    });
                }, 100);
            });
        }
    }
    
    forcePlay();
    
    // При любом клике на странице - тоже пробуем запустить
    document.addEventListener('click', function() {
        if (video.paused) {
            video.muted = false;
            video.volume = 1.0;
            video.play().catch(function(){});
        }
    }, { once: true });
    
    // При скролле - запускаем если видно
    function isElementPartiallyVisible(el) {
        var rect = el.getBoundingClientRect();
        var windowHeight = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < windowHeight - 50 && rect.bottom > 50;
    }
    
    var wasInView = false;
    var userPaused = false;
    
    window.addEventListener('scroll', function() {
        var isInView = isElementPartiallyVisible(videoWrapper);
        
        if (isInView && !wasInView && !userPaused) {
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
    
    video.addEventListener('ended', function() {
        video.currentTime = 0;
        userPaused = false;
    });
});"""

if 'aboutVideo' in js:
    js = re.sub(r'// ===== Video in About section =====.*?// Show button again when video ends\n    \}\n\);\n\}', new_js_block, js, flags=re.DOTALL)
    print("✅ JS обновлён")
else:
    js += "\n" + new_js_block
    print("✅ JS добавлен")

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))

sftp.close()
ssh.close()
print("\n✅ Готово!")
print("   - muted в HTML для автозапуска")
print("   - JS сразу убирает muted и запускает СО ЗВУКОМ")
print("   - 3 попытки запуска с интервалами")
print("   - при клике на страницу - тоже запуск")
print("   - при скролле - запуск со звуком")
