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

# Заменяем блок about-image на видео
old_about_image = """                <div class="about-image">
                    <img src="images/teacher.jpg" alt="Преподаватель английского">
                    <div class="experience-badge">
                        <span class="exp-years">10+</span>
                        <span class="exp-text">лет <br>в профессии</span>
                    </div>
                </div>"""

new_about_video = """                <div class="about-image" id="aboutVideoWrapper">
                    <div class="video-container">
                        <video id="aboutVideo" preload="auto" playsinline muted loop>
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                        </video>
                        <div class="experience-badge">
                            <span class="exp-years">10+</span>
                            <span class="exp-text">лет <br>в профессии</span>
                        </div>
                    </div>
                </div>"""

if old_about_image in html:
    html = html.replace(old_about_image, new_about_video)
    print("✅ Фото заменено на видео в about-image")
else:
    print("❌ Не найден блок about-image")
    # Ищем что там
    idx = html.find('about-image')
    if idx >= 0:
        print(html[idx:idx+500])

# Удаляем старый about-video если был
html = html.replace("""                <div class="about-video" id="aboutVideoWrapper">
                    <div class="video-container">
                        <video id="aboutVideo" preload="auto" playsinline muted loop>
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                        </video>
                        <div class="video-overlay">
                            <span class="video-play-btn">▶</span>
                            <span class="video-label">Видео-презентация</span>
                        </div>
                    </div>
                </div>""", "")

import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=15.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=15.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён")

# ===== 2. Читаем CSS =====
with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# Удаляем старые стили about-video если есть
old_video_css_start = css.find('/* ===== About Video Section =====')
if old_video_css_start >= 0:
    old_video_css_end = css.find('@media (max-width: 768px)', old_video_css_start)
    if old_video_css_end >= 0:
        old_video_css_end = css.find('}', old_video_css_end) + 1
        css = css[:old_video_css_start] + css[old_video_css_end:]
        print("✅ Старые CSS about-video удалены")

# Добавляем новые стили
new_css = """
/* ===== About Video ===== */
.about-image {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.about-image .video-container {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 400px;
}

.about-image video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    border-radius: 20px;
}

.about-image .experience-badge {
    position: absolute;
    bottom: 20px;
    right: 20px;
    background: var(--primary);
    color: white;
    padding: 16px 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 8px 30px rgba(108, 92, 231, 0.4);
    z-index: 2;
}

.about-image .experience-badge .exp-years {
    font-size: 28px;
    font-weight: 800;
    display: block;
    line-height: 1;
}

.about-image .experience-badge .exp-text {
    font-size: 12px;
    opacity: 0.9;
}

@media (max-width: 768px) {
    .about-image .video-container {
        min-height: 250px;
    }
}
"""

css += new_css

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))
print("✅ CSS обновлён")

# ===== 3. Читаем JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Новый JS для видео
new_video_js = """// ===== Video autoplay with sound on scroll =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    
    if (!video || !videoWrapper) return;
    
    function isElementPartiallyVisible(el) {
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < windowHeight - 100 && rect.bottom > 50;
    }
    
    let wasInView = false;
    let userPaused = false;
    
    function tryPlay() {
        if (video.paused && !userPaused) {
            video.muted = false;
            video.volume = 1.0;
            video.play().catch(function(e) {
                console.log('Video play failed:', e);
            });
        }
    }
    
    window.addEventListener('scroll', function() {
        const isInView = isElementPartiallyVisible(videoWrapper);
        
        if (isInView && !wasInView) {
            tryPlay();
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
        }
    });
    
    video.addEventListener('play', function() {
        userPaused = false;
    });
    
    video.addEventListener('ended', function() {
        video.currentTime = 0;
        userPaused = false;
    });
    
    // Пробуем запустить сразу если виден
    setTimeout(function() {
        if (isElementPartiallyVisible(videoWrapper)) {
            tryPlay();
            wasInView = true;
        }
    }, 500);
});"""

# Заменяем старый блок
start = js.find('// ===== Video in About section')
if start >= 0:
    end = js.find('// =====', start + 10)
    if end < 0:
        end = len(js)
    js = js[:start] + new_video_js + js[end:]
    print("✅ JS видео блок заменён")
else:
    # Ищем старый блок
    start2 = js.find('// ===== Video autoplay')
    if start2 >= 0:
        end2 = js.find('// =====', start2 + 10)
        if end2 < 0:
            end2 = len(js)
        js = js[:start2] + new_video_js + js[end2:]
        print("✅ JS видео блок заменён (вариант 2)")
    else:
        js += "\n" + new_video_js
        print("✅ JS видео блок добавлен")

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n🎉 Готово! Фото заменено на видео с автозапуском со звуком при скролле")
