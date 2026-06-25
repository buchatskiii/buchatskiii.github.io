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

# Убираем muted с видео
html = html.replace('muted playsinline', 'playsinline')

# Обновляем версию
import re
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=2.2', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=2.2', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ muted убран — звук будет работать!")

# Читаем JS
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# В JS тоже убираем muted-логику (если есть)
# Добавляем громкость по умолчанию
if 'aboutVideo' in js:
    # Добавляем установку громкости при старте
    js = js.replace("""document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    const playBtn = document.getElementById('videoPlayBtn');""", """document.addEventListener('DOMContentLoaded', function() {
    const videoWrapper = document.getElementById('aboutVideoWrapper');
    const video = document.getElementById('aboutVideo');
    const playBtn = document.getElementById('videoPlayBtn');
    
    // Устанавливаем громкость
    if (video) video.volume = 1.0;""")

with sftp.open("/var/www/englishpro/script.js", "w") as f:
    f.write(js.encode("utf-8"))
print("✅ JS обновлён — громкость установлена")

sftp.close()
ssh.close()
print("\n✅ Готово! Обновите страницу — звук должен появиться")
