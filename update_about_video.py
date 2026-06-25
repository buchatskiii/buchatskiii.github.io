import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

# ========== 1. Читаем HTML ==========
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# ========== 2. Меняем секцию "Обо мне" — заменяем фото на видео ==========
old_about = """                <div class="about-image">
                    <img src="https://images.unsplash.com/photo-1580894732444-8ecded7900cd?w=500&h=600&fit=crop&crop=face" alt="Преподаватель английского">
                    <div class="experience-badge">
                        <span class="exp-years">10+</span>
                        <span class="exp-text">лет <br>в профессии</span>
                    </div>
                </div>"""

new_about = """                <div class="about-image">
                    <div class="about-video-wrapper" id="aboutVideoWrapper">
                        <video class="about-video" id="aboutVideo" muted playsinline preload="auto" poster="/images/video-poster.jpg">
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                            Ваш браузер не поддерживает видео.
                        </video>
                        <div class="video-play-btn" id="videoPlayBtn">
                            <span class="play-icon">▶</span>
                            <span class="play-text">Нажмите, чтобы посмотреть обращение</span>
                        </div>
                    </div>
                    <div class="experience-badge">
                        <span class="exp-years">10+</span>
                        <span class="exp-text">лет <br>в профессии</span>
                    </div>
                </div>"""

html = html.replace(old_about, new_about)

# ========== 3. Удаляем отдельную видео-секцию (она больше не нужна) ==========
import re
html = re.sub(r'<!-- Video Section -->.*?<section class="contact section"', '<section class="contact section"', html, flags=re.DOTALL)

# ========== 4. Сохраняем HTML ==========
with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён — видео вставлено в блок 'Обо мне'")

# ========== 5. Читаем CSS ==========
with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# ========== 6. Удаляем старые стили для video-section ==========
css = re.sub(r'/\* Video Section \*/.*?background: #000;\n}', '', css, flags=re.DOTALL)

# ========== 7. Добавляем новые стили для about-video ==========
new_css = """
/* About Video */
.about-video-wrapper {
    position: relative;
    width: 100%;
    border-radius: 20px;
    overflow: hidden;
    cursor: pointer;
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

/* Анимация пульсации для кнопки play */
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.6); }
    100% { box-shadow: 0 0 0 30px rgba(99, 102, 241, 0); }
}

.video-play-btn .play-icon {
    animation: pulse 2s infinite;
}
"""

css += new_css

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))
print("✅ CSS обновлён")

# ========== 8. Читаем JS ==========
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# ========== 9. Добавляем JS для автовоспроизведения при скролле и нажатии ==========
video_js = """
// ===== Video in About section =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    const playBtn = document.getElementById('videoPlayBtn');
    
    if (!video || !videoWrapper) return;
    
    // Функция проверки видимости элемента
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // Функция проверки частичной видимости
    function isElementPartiallyVisible(el) {
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < windowHeight - 100 && rect.bottom > 100;
    }
    
    // Воспроизведение при нажатии на кнопку
    playBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        video.play();
        videoWrapper.classList.add('playing');
        playBtn.style.display = 'none';
    });
    
    // Клик по видео для паузы/воспроизведения
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
    
    // Автовоспроизведение при скролле до блока
    let autoPlayed = false;
    window.addEventListener('scroll', function() {
        if (!autoPlayed && isElementPartiallyVisible(videoWrapper)) {
            // Прокручиваем до блока "Обо мне" — запускаем видео
            video.play().then(() => {
                videoWrapper.classList.add('playing');
                playBtn.style.display = 'none';
                autoPlayed = true;
            }).catch(() => {
                // Автовоспроизведение заблокировано браузером — ждём клика
            });
        }
    }, { passive: true });
    
    // При нажатии на ссылку "Обо мне" в навигации — скроллим и запускаем
    document.querySelectorAll('a[href="#about"]').forEach(link => {
        link.addEventListener('click', function(e) {
            setTimeout(function() {
                if (isElementPartiallyVisible(videoWrapper) && video.paused) {
                    video.play().then(() => {
                        videoWrapper.classList.add('playing');
                        playBtn.style.display = 'none';
                        autoPlayed = true;
                    }).catch(() => {});
                }
            }, 800);
        });
    });
    
    // Когда видео закончилось — показываем кнопку снова
    video.addEventListener('ended', function() {
        videoWrapper.classList.remove('playing');
        playBtn.style.display = 'flex';
        autoPlayed = false;
    });
});
"""

js += video_js

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))
print("✅ JS обновлён — автовоспроизведение при скролле и нажатии на 'Обо мне'")

sftp.close()
ssh.close()
print("\n✅ Готово! Обновите страницу http://139.100.234.22/")
