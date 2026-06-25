import paramiko
import re
import random

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

# Найдём всё, что связано с aboutVideo
idx = html.find('aboutVideo')
if idx >= 0:
    # Покажем 500 символов вокруг
    start = max(0, idx - 200)
    end = min(len(html), idx + 500)
    print("=== КОНТЕКСТ ВОКРУГ aboutVideo ===")
    print(html[start:end])
    print("=== КОНЕЦ КОНТЕКСТА ===")
else:
    print("aboutVideo не найден!")

# Найдём about-video
idx2 = html.find('about-video')
if idx2 >= 0:
    start = max(0, idx2 - 100)
    end = min(len(html), idx2 + 800)
    print("\n=== КОНТЕКСТ ВОКРУГ about-video ===")
    print(html[start:end])
    print("=== КОНЕЦ КОНТЕКСТА ===")
else:
    print("about-video не найден!")

sftp.close()
ssh.close()
