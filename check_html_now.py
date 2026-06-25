import paramiko

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

# Найдём блок about-image
import re
match = re.search(r'<div class="about-image">(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
if match:
    print("=== Содержимое about-image ===")
    print(match.group(0))
else:
    print("about-image не найден!")
    # Поищем любые упоминания about
    for m in re.finditer(r'about[^>]*>', html):
        print(m.group())

sftp.close()
ssh.close()
