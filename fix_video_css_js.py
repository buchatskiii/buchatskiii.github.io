import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

# ===== 1. Проверяем видео на сервере =====
stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/englishpro/videos/")
print("Видео на сервере:")
print(stdout.read().decode())

# ===== 2. Читаем CSS =====
with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# Удаляем старые стили video-section если есть
import re
css = re.sub(r'/\* Video Section \*/.*?background: #000;\n}', '', css, flags=re.DOTALL)

# Добавляем стили для about-video если их нет
if 'about-video-wrapper' not in css:
    css += """
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

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.6); }
    100% { box-shadow: 0 0 0 30px rgba(99, 102, 241, 0); }
}

.video-play-btn .play-icon {
    animation: pulse 2s infinite;
}
"""
    print("✅ CSS-стили добавлены")
else:
    print("✅ CSS-стили уже есть")

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))

# ===== 3. Читаем JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Добавляем JS для видео если его нет
if 'aboutVideo' not in js:
    js += """
// ===== Video in About section =====
document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    const playBtn = document.getElementById('videoPlayBtn');
    
    if (!video || !videoWrapper) return;
    
    function isElementPartiallyVisible(el) {
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < windowHeight - 100 && rect.bottom > 100;
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
    
    // Auto-play on scroll
    let autoPlayed = false;
    window.addEventListener('scroll', function() {
        if (!autoPlayed && isElementPartiallyVisible(videoWrapper)) {
            video.play().then(() => {
                videoWrapper.classList.add('playing');
                playBtn.style.display = 'none';
                autoPlayed = true;
            }).catch(() => {});
        }
    }, { passive: true });
    
    // Play when clicking "Обо мне" nav link
    document.querySelectorAll('a[href="#about"]').forEach(link => {
        link.addEventListener('click', function() {
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
    
    // Show button again when video ends
    video.addEventListener('ended', function() {
        videoWrapper.classList.remove('playing');
        playBtn.style.display = 'flex';
        autoPlayed = false;
    });
});
"""
    print("✅ JS-код добавлен")
else:
    print("✅ JS-код уже есть")

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))

sftp.close()
ssh.close()
print("\n✅ Готово! Обновите http://139.100.234.22/")
