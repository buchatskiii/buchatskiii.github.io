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

# Находим и заменяем весь блок about-content
import re

old_about = r'''<div class="about-content">.*?<div class="about-text">'''

match = re.search(old_about, html, re.DOTALL)
if match:
    print("Найден старый блок about-content, заменяю...")
    
    new_about_start = '''<div class="about-content">
                <div class="about-image">
                    <div class="about-video-wrapper" id="aboutVideoWrapper">
                        <video class="about-video" id="aboutVideo" autoplay muted playsinline preload="auto" controls>
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                            Ваш браузер не поддерживает видео.
                        </video>
                    </div>
                    <div class="experience-badge">
                        <span class="exp-years">10+</span>
                        <span class="exp-text">лет <br>в профессии</span>
                    </div>
                </div>
                <div class="about-text">'''
    
    html = html.replace(match.group(0), new_about_start)
    print("✅ HTML about-content исправлен")
else:
    print("❌ Не удалось найти блок about-content")

# Обновляем версию
html = html.replace('styles.css?v=3.0', 'styles.css?v=4.0')
html = html.replace('script.js?v=3.0', 'script.js?v=4.0')

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))

# ===== 2. Читаем CSS =====
with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# Проверяем стили для about-content
if '.about-content' in css:
    print("✅ CSS about-content найден")
else:
    print("❌ CSS about-content не найден!")

# Добавляем/обновляем стили для about-image и about-video
# Удаляем старые стили about-video если есть
css = re.sub(r'/\* About Video \*/.*?\.about-video \{[^}]*\}', '', css, flags=re.DOTALL)

# Добавляем правильные стили
css += """
/* About Video - исправлено */
.about-image {
    flex: 1;
    min-width: 300px;
    position: relative;
}

.about-video-wrapper {
    position: relative;
    width: 100%;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(99, 102, 241, 0.2);
}

.about-video {
    width: 100%;
    display: block;
    border-radius: 20px;
    max-height: 500px;
    object-fit: cover;
    background: #1a1a2e;
}

.about-content {
    display: flex;
    align-items: center;
    gap: 60px;
}

.about-text {
    flex: 1;
    min-width: 300px;
}

@media (max-width: 992px) {
    .about-content {
        flex-direction: column;
    }
}
"""

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))
print("✅ CSS обновлён")

# ===== 3. Читаем JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Заменяем блок video JS на новый — с controls и звуком
new_js_block = """// ===== Video in About section =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    
    if (!video || !videoWrapper) return;
    
    // Пытаемся включить звук при первом взаимодействии пользователя
    function enableSound() {
        video.muted = false;
        video.volume = 1.0;
        document.removeEventListener('click', enableSound);
        document.removeEventListener('scroll', enableSound);
        document.removeEventListener('touchstart', enableSound);
    }
    
    document.addEventListener('click', enableSound);
    document.addEventListener('scroll', enableSound);
    document.addEventListener('touchstart', enableSound);
    
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
    
    // Scroll logic: pause when out of view, play when in view
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
    
    // Play when clicking "Обо мне" nav link
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

# Удаляем старый блок и вставляем новый
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
print("\n✅ Готово! Всё исправлено:")
print("   - Верстка about-content восстановлена")
print("   - Добавлены controls для листания видео")
print("   - Звук включится при первом клике/скролле по странице")
