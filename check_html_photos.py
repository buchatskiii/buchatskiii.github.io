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

# Ищем все src
matches = re.findall(r'src="([^"]+)"', html)
print("=== Все src атрибуты ===")
for m in matches:
    if 'unsplash' in m or '/images/' in m or 'http' in m:
        print(f"  {m}")

# Ищем student-photo блоки
idx = html.find('result-card')
while idx >= 0:
    block = html[idx:idx+500]
    # Ищем src в этом блоке
    srcs = re.findall(r'src="([^"]+)"', block)
    for s in srcs:
        print(f"  Фото в result-card: {s}")
    idx = html.find('result-card', idx + 1)

# Ищем testimonial блоки
idx = html.find('testimonial-card')
while idx >= 0:
    block = html[idx:idx+500]
    srcs = re.findall(r'src="([^"]+)"', block)
    for s in srcs:
        print(f"  Фото в testimonial: {s}")
    idx = html.find('testimonial-card', idx + 1)

sftp.close()
ssh.close()
