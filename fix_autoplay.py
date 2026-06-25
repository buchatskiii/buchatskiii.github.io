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

# Меняем видео-тег: убираем кнопку play, добавляем autoplay
old_video_html = """<div class="about-video-wrapper" id="aboutVideoWrapper">
                        <video class="about-video" id="aboutVideo" muted playsinline preload="auto" poster="/images/video-poster.jpg">
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                            Ваш браузер не поддерживает видео.
                        </video>
                        <div class="video-play-btn" id="videoPlayBtn">
                            <span class="play-icon">▶</span>
                            <span class="play-text">Нажмите, чтобы посмотреть обращение</span>
                        </div>
                    </div>"""

new_video_html = """<div class="about-video-wrapper" id="aboutVideoWrapper">
                        <video class="about-video" id="aboutVideo" autoplay muted playsinline preload="auto">
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                            Ваш браузер не поддерживает видео.
                        </video>
                    </div>"""

if old_video_html in html:
    html = html.replace(old_video_html, new_video_html)
    print("✅ HTML обновлён — autoplay добавлен, кнопка Play убрана")
else:
    print("⚠️ Точное совпадение не найдено, ищу альтернативу...")
    # Найдём блок с aboutVideoWrapper
    import re
    match = re.search(r'<div class="about-video-wrapper"[^>]*>.*?<video[^>]*>.*?Ваш браузер не поддерживает видео\..*?</video>.*?</div>', html, re.DOTALL)
    if match:
        print("Найден блок видео, заменяю...")
        html = html.replace(match.group(0), new_video_html)
        print("✅ HTML обновлён")
    else:
        print("❌ Не удалось найти блок видео в HTML!")

# Обновляем версию
html = html.replace('styles.css?v=2.3', 'styles.css?v=3.0')
html = html.replace('script.js?v=2.3', 'script.js?v=3.0')

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))

# ===== 2. Читаем CSS =====
with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# Убираем стили для play-btn
css = css.replace("""
.video-play-btn {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    z-index: 10;
    transition: all 0.3s ease;
}

.video-play-btn .play-icon {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    color: white;
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
    transition: all 0.3s ease;
}

.video-play-btn .play-text {
    color: white;
    font-size: 14px;
    font-weight: 500;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    background: rgba(0,0,0,0.6);
    padding: 8px 20px;
    border-radius: 20px;
    white-space: nowrap;
}

.about-video-wrapper:hover .play-icon {
    transform: scale(1.1);
    box-shadow: 0 15px 40px rgba(99, 102, 241, 0.6);
}

.about-video-wrapper.playing .video-play-btn {
    opacity: 0;
    pointer-events: none;
}

.about-video-wrapper.playing:hover .video-play-btn {
    opacity: 1;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.6); }
    100% { box-shadow: 0 0 0 30px rgba(99, 102, 241, 0); }
}

.video-play-btn .play-icon {
    animation: pulse 2s infinite;
}
""", "")

# Добавляем простые стили для about-video
if 'about-video-wrapper' not in css:
    css += """
/* About Video */
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
"""

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))
print("✅ CSS обновлён — стили для play-btn удалены")

# ===== 3. Читаем JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Заменяем весь блок video JS на новый — без кнопки play
old_js = """// ===== Video in About section =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    const playBtn = document.getElementById('videoPlayBtn');
    
    if (!video || !videoWrapper) return;
    
    // Устанавливаем громкость
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
    
    // Play on button click
    playBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        video.play();
        videoWrapper.classList.add('playing');
        playBtn.style.display = 'none';
    });
    
    // Click on video to pause/play
    video.addEventListener('click', function() {
        if (video.paused) {
            video.play();
            videoWrapper.classList.add('playing');
            playBtn.style.display = 'none';
        } else {
            video.pause();
            videoWrapper.classList.remove('playing');
            playBtn.style.display = 'flex';
        }
    });
    
    // Scroll logic: pause when out of view, play when in view
    let wasInView = false;
    let userPaused = false;
    
    window.addEventListener('scroll', function() {
        const isInView = isElementPartiallyVisible(videoWrapper);
        const isOutOfView = isElementFullyOutOfView(videoWrapper);
        
        if (isInView && !wasInView && !userPaused) {
            // Видео появилось в зоне видимости — запускаем
            video.play().then(() => {
                videoWrapper.classList.add('playing');
                playBtn.style.display = 'none';
            }).catch(() => {});
        } else if (isOutOfView && wasInView) {
            // Видео ушло с экрана — ставим на паузу
            if (!video.paused) {
                video.pause();
                videoWrapper.classList.remove('playing');
                playBtn.style.display = 'flex';
            }
        }
        
        wasInView = isInView;
    }, { passive: true });
    
    // Если пользователь сам поставил на паузу — не запускаем автоматически
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
                    video.play().then(() => {
                        videoWrapper.classList.add('playing');
                        playBtn.style.display = 'none';
                        userPaused = false;
                    }).catch(() => {});
                }
            }, 800);
        });
    });
    
    // Show button again when video ends
    video.addEventListener('ended', function() {
        videoWrapper.classList.remove('playing');
        playBtn.style.display = 'flex';
        userPaused = false;
    });
});"""

new_js = """// ===== Video in About section =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    
    if (!video || !videoWrapper) return;
    
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
            // Видео появилось в зоне видимости — запускаем
            video.play().catch(() => {});
        } else if (isOutOfView && wasInView) {
            // Видео ушло с экрана — ставим на паузу
            if (!video.paused) {
                video.pause();
            }
        }
        
        wasInView = isInView;
    }, { passive: true });
    
    // Если пользователь сам поставил на паузу — не запускаем автоматически
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
    
    // Когда видео закончилось — перематываем на начало для повторного автозапуска
    video.addEventListener('ended', function() {
        video.currentTime = 0;
        userPaused = false;
    });
});"""

if old_js in js:
    js = js.replace(old_js, new_js)
    print("✅ JS обновлён — полный автозапуск без кнопки Play")
else:
    print("⚠️ Старый JS не найден, ищу через regex...")
    import re
    js = re.sub(r'// ===== Video in About section =====.*?// Show button again when video ends\n    \}\n\);\n\}', new_js, js, flags=re.DOTALL)
    print("✅ JS заменён через regex")

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))

sftp.close()
ssh.close()
print("\n✅ Готово! Видео будет запускаться автоматически при скролле до блока 'Обо мне'")
print("   (из-за политики браузеров звук может быть muted при первом автозапуске)")
print("   Звук можно включить через интерфейс самого плеера")
