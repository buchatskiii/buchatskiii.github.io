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

with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Video тег
v = re.search(r'<video[^>]*>', html)
print(f"Video тег: {v.group() if v else 'НЕ НАЙДЕН'}")

# Скрипт
m = re.search(r'<script>\n\(function\(\)[\s\S]*?</script>', html)
if m:
    script = m.group()
    print(f"\nСкрипт (первые 200 символов):")
    print(script[:200])
    print(f"\nСкрипт (последние 200 символов):")
    print(script[-200:])
    
    # Проверки
    checks = [
        ('IntersectionObserver', 'IntersectionObserver'),
        ('observer', 'observer'),
        ('tryPlay', 'tryPlay'),
        ('userStopped', 'userStopped'),
        ('autoplay', 'autoplay в скрипте'),
        ('scroll', 'scroll'),
    ]
    for keyword, desc in checks:
        if keyword in script:
            print(f"❌ {desc} ЕСТЬ в скрипте!")
        else:
            print(f"✅ {desc} НЕТ в скрипте")
else:
    print("❌ Скрипт не найден!")

# Версия
v_match = re.search(r'script\.js\?v=([\d.]+)', html)
if v_match:
    print(f"\nВерсия: {v_match.group(1)}")

sftp.close()
ssh.close()
