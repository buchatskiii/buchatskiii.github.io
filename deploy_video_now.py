import paramiko
import os

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

video_file = r"C:\Users\dlyav\Desktop\english-tutor\videos\повелитель вселенной.MP4"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Upload video
remote_path = "/var/www/englishpro/videos/povelitel_vselennoy.mp4"
sftp = ssh.open_sftp()
print("Загружаю видео на сервер...")
sftp.put(video_file, remote_path)
sftp.close()
print("✅ Видео загружено!")

# Read current index.html
sftp = ssh.open_sftp()
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Add video section before contact section
video_section = """    <!-- Video Section -->
    <section class="video-section section" id="video">
        <div class="container">
            <div class="section-header">
                <span class="section-tag">Видео</span>
                <h2>Посмотрите <span class="highlight">моё обращение</span></h2>
                <p>Узнайте больше о моём подходе к преподаванию</p>
            </div>
            <div class="video-wrapper">
                <video class="video-player" controls poster="/images/video-poster.jpg">
                    <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                    Ваш браузер не поддерживает видео.
                </video>
            </div>
        </div>
    </section>

"""

html = html.replace('    <section class="contact section"', video_section + '    <section class="contact section"')

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
sftp.close()
print("✅ Видео-секция добавлена на сайт!")

ssh.close()
print("\n✅ Готово! Обновите страницу http://139.100.234.22/")
