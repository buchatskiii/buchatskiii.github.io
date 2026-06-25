import paramiko
import re

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

# Проверяем video тег
m = re.search(r'<video[^>]*>', html)
print(f"Video тег: {m.group() if m else 'НЕ НАЙДЕН!'}")

# Проверяем скрипт
scripts = re.findall(r'<script>\n\(function\(\)[\s\S]*?</script>', html)
print(f"Найдено скриптов: {len(scripts)}")
if scripts:
    # Покажем первые 500 символов
    print(f"Скрипт (первые 500 символов):\n{scripts[0][:500]}")

# Проверяем есть ли userPaused
if 'userPaused' in html:
    print("✅ userPaused найден в HTML")
else:
    print("❌ userPaused НЕ найден в HTML")

# Проверяем есть ли setInterval
if 'setInterval' in html:
    print("❌ setInterval всё ещё есть в HTML!")
else:
    print("✅ setInterval отсутствует")

# Проверяем muted
if 'muted' in html.split('<video')[1].split('>')[0] if '<video' in html else '':
    print("❌ muted всё ещё есть в video теге!")
else:
    print("✅ muted отсутствует в video теге")

sftp.close()
ssh.close()
