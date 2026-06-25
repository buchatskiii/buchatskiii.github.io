import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# Читаем HTML
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Ищем секцию about - добавляем видео после about-text
video_block = """
                <div class="about-video" id="aboutVideoWrapper">
                    <div class="video-container">
                        <video id="aboutVideo" preload="auto" playsinline muted loop>
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                        </video>
                        <div class="video-overlay">
                            <span class="video-play-btn">▶</span>
                            <span class="video-label">Видео-презентация</span>
                        </div>
                    </div>
                </div>"""

# Вставляем видео после about-text
if 'about-video' not in html:
    html = html.replace('</div>\n            </div>\n        </div>\n    </section>\n\n    <!-- Results Section -->', 
                        f'{video_block}\n            </div>\n        </div>\n    </section>\n\n    <!-- Results Section -->')
    print("✅ Видео-блок добавлен в HTML")
else:
    print("ℹ️ Видео-блок уже есть в HTML")

# Обновляем версию
import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=13.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=13.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))

# Читаем CSS и добавляем стили для видео
with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

video_css = """
/* ===== About Video Section ===== */
.about-video {
    margin-top: 40px;
    width: 100%;
    max-width: 560px;
}

.video-container {
    position: relative;
    width: 100%;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    cursor: pointer;
}

.video-container video {
    width: 100%;
    display: block;
    border-radius: 16px;
}

.video-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 20px;
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
    display: flex;
    align-items: center;
    gap: 12px;
    pointer-events: none;
}

.video-play-btn {
    width: 48px;
    height: 48px;
    background: var(--primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 20px;
    transition: transform 0.3s;
}

.video-container:hover .video-play-btn {
    transform: scale(1.1);
}

.video-label {
    color: white;
    font-size: 14px;
    font-weight: 500;
    text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

@media (max-width: 768px) {
    .about-video {
        max-width: 100%;
    }
}
"""

if 'About Video Section' not in css:
    css += video_css
    print("✅ CSS для видео добавлен")

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n✅ Готово! Видео добавлено в секцию 'Обо мне'")
