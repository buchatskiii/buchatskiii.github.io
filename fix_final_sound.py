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

# Убираем muted полностью
html = html.replace(
    'autoplay muted playsinline preload="auto" controls',
    'autoplay playsinline preload="auto" controls'
)

# Обновляем версию
import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=5.1', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=5.1', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён — muted убран")

# ===== 2. Читаем JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Простой JS: при скролле запускаем видео со звуком
new_js_block = """// ===== Video in About section =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    
    if (!video || !videoWrapper) return;
    
    video.volume = 1.0;
    
    function isElementPartiallyVisible(el) {
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < windowHeight - 100 && rect.bottom > 100;
    }
    
    function isElementFullyOutOfView(el) {
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        return rect.bottom < 0 || rect.top > windowHeight;
    }
    
    let wasInView = false;
    let userPaused = false;
    
    window.addEventListener('scroll', function() {
        const isInView = isElementPartiallyVisible(videoWrapper);
        const isOutOfView = isElementFullyOutOfView(videoWrapper);
        
        if (isInView && !wasInView && !userPaused) {
            video.play().catch(() => {});
        } else if (isOutOfView && wasInView) {
            if (!video.paused) {
                video.pause();
            }
        }
        
        wasInView = isInView;
    }, { passive: true });
    
    video.addEventListener('pause', function() {
        if (!isElementPartiallyVisible(videoWrapper)) {
            userPaused = false;
        } else {
            userPaused = true;
        }
    });
    
    video.addEventListener('play', function() {
        userPaused = false;
    });
    
    document.querySelectorAll('a[href="#about"]').forEach(link => {
        link.addEventListener('click', function() {
            setTimeout(function() {
                if (isElementPartiallyVisible(videoWrapper) && video.paused) {
                    video.play().catch(() => {});
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
    js = re.sub(r'// ===== Video in About section =====.*?// Show button again when video ends\n    \}\n\);\n\}', new_js_block, js, flags=re.DOTALL)
    print("✅ JS обновлён")
else:
    js += "\n" + new_js_block
    print("✅ JS добавлен")

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))

sftp.close()
ssh.close()
print("\n✅ Готово! muted полностью убран, видео будет со звуком")
