import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# ===== 1. Проверяем конфиг Nginx =====
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/default")
nginx_conf = stdout.read().decode()
print("=== Nginx config ===")
print(nginx_conf)

# ===== 2. Добавляем MIME типы для видео =====
if 'video/mp4' not in nginx_conf:
    # Добавляем в секцию server
    nginx_conf = nginx_conf.replace(
        "server {",
        """server {
    # Video MIME types
    types {
        video/mp4 mp4;
        video/webm webm;
        video/ogg ogv;
    }"""
    )
    
    # Записываем
    stdin, stdout, stderr = ssh.exec_command("cat > /etc/nginx/sites-enabled/default << 'NGINX_EOF'\n" + nginx_conf + "\nNGINX_EOF")
    print(stdout.read().decode())
    print(stderr.read().decode())
    print("✅ MIME типы добавлены в Nginx")

# ===== 3. Проверяем HTML =====
sftp = ssh.open_sftp()
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Проверяем текущее состояние video
idx = html.find('aboutVideo')
if idx >= 0:
    print("\n=== Текущий video тег ===")
    print(html[idx-50:idx+300])

# Делаем простой HTML5 video с controls
old_video = html[html.find('<video id="aboutVideo"'):html.find('</video>', html.find('<video id="aboutVideo"')) + 8]
new_video = '''<video id="aboutVideo" preload="auto" playsinline loop controls
    style="width:100%;height:100%;object-fit:cover;border-radius:20px;cursor:pointer;">
    <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
    Ваш браузер не поддерживает видео
</video>'''

html = html.replace(old_video, new_video)

import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=17.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=17.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("\n✅ HTML video обновлён (добавлены controls)")

# ===== 4. Обновляем JS =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

new_js = """// ===== Video autoplay with sound =====
document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('aboutVideo');
    if (!video) return;
    
    function isVisible(el) {
        const rect = el.getBoundingClientRect();
        const wh = window.innerHeight || document.documentElement.clientHeight;
        return rect.top < wh - 50 && rect.bottom > 50;
    }
    
    let played = false;
    
    function tryPlay() {
        if (!played) {
            video.muted = false;
            video.volume = 1.0;
            var promise = video.play();
            if (promise !== undefined) {
                promise.then(function() {
                    played = true;
                    console.log('Video playing with sound');
                }).catch(function(e) {
                    console.log('Play blocked:', e);
                    // Если заблокировали - ждём клика
                    video.muted = true;
                    video.play().then(function() {
                        played = true;
                    }).catch(function(){});
                });
            }
        }
    }
    
    // При скролле
    window.addEventListener('scroll', function() {
        if (isVisible(video) && !played) {
            tryPlay();
        }
    }, { passive: true });
    
    // Сразу проверяем
    setTimeout(function() {
        if (isVisible(video)) {
            tryPlay();
        }
    }, 500);
    
    // По клику включаем звук если muted
    video.addEventListener('click', function() {
        if (video.muted) {
            video.muted = false;
            video.volume = 1.0;
        }
        if (video.paused) {
            video.play();
        } else {
            video.pause();
        }
    });
});"""

start = js.find('// ===== Video')
if start >= 0:
    end = js.find('// =====', start + 10)
    if end < 0:
        end = len(js)
    js = js[:start] + new_js + js[end:]
else:
    js += "\n" + new_js

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))
print("✅ JS обновлён")

sftp.close()

# ===== 5. Перезапускаем nginx =====
ssh.exec_command("systemctl restart nginx")
ssh.close()

print("\n🎉 Готово! Видео должно работать. Проверьте на https://beklox.ru/")
print("   - Если звук не включится автоматически - нажмите на видео")
