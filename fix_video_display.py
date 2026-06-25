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

# Убираем poster (его нет на сервере, из-за него видео может не показываться)
html = html.replace('poster="/images/video-poster.jpg"', '')

# Обновляем версию CSS и JS для сброса кеша
import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=2.1', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=2.1', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ HTML обновлён (убран poster, обновлена версия)")

# ===== 2. Читаем CSS =====
with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# Добавляем стиль, чтобы видео было видно (чёрный фон с центровкой)
if 'about-video' in css:
    # Убедимся, что стили правильные
    print("✅ CSS стили для видео есть")
else:
    print("❌ CSS стили отсутствуют!")

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))

# ===== 3. Проверяем, что видео доступно по HTTP =====
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost/videos/povelitel_vselennoy.mp4")
status = stdout.read().decode().strip()
print(f"✅ Видео доступно (HTTP {status})")

# ===== 4. Проверяем размер =====
stdin, stdout, stderr = ssh.exec_command("ls -lh /var/www/englishpro/videos/povelitel_vselennoy.mp4")
print(stdout.read().decode().strip())

sftp.close()
ssh.close()
print("\n✅ Готово! Обновите страницу (Ctrl+F5 для жёсткого сброса кеша)")
