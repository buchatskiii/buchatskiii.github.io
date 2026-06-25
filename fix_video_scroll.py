import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

# Читаем JS
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# Находим и заменяем весь блок video JS
old_js_block = """// ===== Video in About section =====
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
});"""

new_js_block = """// ===== Video in About section =====
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

if old_js_block in js:
    js = js.replace(old_js_block, new_js_block)
    print("✅ JS-блок заменён на новый с логикой скролла")
else:
    print("⚠️ Старый блок не найден, ищу альтернативу...")
    # Если блок немного отличается, найдём по ключевым словам
    if 'aboutVideo' in js:
        # Удаляем старый блок и вставляем новый
        import re
        js = re.sub(r'// ===== Video in About section =====.*?// Show button again when video ends\n    \}\n\);\n\}', new_js_block, js, flags=re.DOTALL)
        print("✅ JS заменён через regex")
    else:
        print("❌ aboutVideo не найден в JS!")
        js += "\n" + new_js_block
        print("✅ JS добавлен в конец")

# Обновляем версию
import re
html_path = "/var/www/englishpro/index.html"
with sftp.open(html_path, "r") as f:
    html = f.read().decode("utf-8")

html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=2.3', html)

with sftp.open(html_path, "w") as f:
    f.write(html.encode("utf-8"))

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))

sftp.close()
ssh.close()
print("\n✅ Готово! Видео будет останавливаться при уходе с экрана и возобновляться при возвращении")
