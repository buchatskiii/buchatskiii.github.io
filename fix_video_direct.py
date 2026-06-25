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

# Находим точное место для вставки видео - после закрытия about-achievements
# Ищем конец about-text
video_block = """                    </div>
                </div>
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
                </div>
            </div>
        </div>
    </section>

    <section class="results section" id="results">"""

# Ищем конец about-text
old_end = '                    </div>\n                </div>\n            </div>\n        </div>\n    </section>\n\n    <section class="results section" id="results">'

if old_end in html:
    html = html.replace(old_end, video_block)
    print("✅ Видео-блок вставлен!")
else:
    print("❌ Не найден конец about секции")
    # Пробуем другой вариант
    old_end2 = '                </div>\n            </div>\n        </div>\n    </section>\n\n    <section class="results section" id="results">'
    if old_end2 in html:
        html = html.replace(old_end2, video_block)
        print("✅ Видео-блок вставлен (вариант 2)!")
    else:
        print("❌ Вариант 2 тоже не найден")
        # Покажем что вокруг
        idx = html.find('id="results"')
        print(f"\nКонтекст вокруг results:")
        print(html[idx-500:idx+100])

# Обновляем версию
import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=14.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=14.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n✅ Готово!")
