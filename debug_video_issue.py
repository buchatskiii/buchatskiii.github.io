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

# Найдём весь скрипт
m = re.search(r'<script>\n\(function\(\)[\s\S]*?</script>', html)
if m:
    script = m.group()
    print("=== ПОЛНЫЙ СКРИПТ ===")
    print(script)
    print("=== КОНЕЦ СКРИПТА ===")
    
    # Проверяем ключевые моменты
    checks = [
        ('userPaused', 'userPaused'),
        ('scriptPausing', 'scriptPausing'),
        ('IntersectionObserver', 'IntersectionObserver'),
        ('scroll', 'scroll обработчик'),
        ('setInterval', 'setInterval'),
        ('muted', 'muted в скрипте'),
    ]
    for keyword, desc in checks:
        if keyword in script:
            print(f"✅ {desc} найден")
        else:
            print(f"❌ {desc} НЕ найден")
else:
    print("❌ Скрипт не найден!")

# Проверяем video тег
v = re.search(r'<video[^>]*>', html)
if v:
    print(f"\nVideo тег: {v.group()}")

sftp.close()
ssh.close()
