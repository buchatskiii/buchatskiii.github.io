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

# Меняем: Алина (4.jpg) <-> Артём (3.jpg)
# Алина М. (94 балла) - сейчас /images/4.jpg, нужно /images/3.jpg
# Артём С. (92 балла ОГЭ) - сейчас /images/3.jpg, нужно /images/4.jpg

# Сначала меняем на временные метки, чтобы не пересеклись
html = html.replace('/images/4.jpg', '/images/TEMP_SWAP.jpg')
html = html.replace('/images/3.jpg', '/images/4.jpg')
html = html.replace('/images/TEMP_SWAP.jpg', '/images/3.jpg')

# Обновляем версию
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=26.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=26.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ Алина и Артём поменялись аватарками")

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("🎉 Готово!")
