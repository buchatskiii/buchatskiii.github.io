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

# Найдём блок about-content
import re
match = re.search(r'<div class="about-content">(.*?)</div>\s*</div>\s*</div>\s*</section>', html, re.DOTALL)
if match:
    print("=== about-content ===")
    print(match.group(0)[:2000])
else:
    print("about-content не найден!")

sftp.close()
ssh.close()
