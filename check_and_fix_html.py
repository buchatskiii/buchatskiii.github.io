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
v = re.search(r'<video[^>]*>', html)
print(f"Video тег: {v.group() if v else 'НЕ НАЙДЕН'}")

# Проверяем autoplay в теге
if 'autoplay' in html.split('<video')[1].split('>')[0]:
    print("❌ autoplay всё ещё в HTML теге!")
else:
    print("✅ autoplay НЕТ в HTML теге")

# Проверяем скрипт
m = re.search(r'<script>\n\(function\(\)[\s\S]*?</script>', html)
if m:
    script = m.group()
    if 'observer.disconnect' in script:
        print("✅ observer.disconnect есть в скрипте")
    else:
        print("❌ observer.disconnect НЕТ в скрипте")
    
    if 'forever' in script:
        print("✅ forever pause версия")
    else:
        print("❌ НЕ forever pause версия")
else:
    print("❌ Скрипт не найден!")

# Проверяем версию
v_match = re.search(r'script\.js\?v=([\d.]+)', html)
if v_match:
    print(f"Версия: {v_match.group(1)}")

sftp.close()
ssh.close()
