import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

# ===== 1. Читаем CSS =====
with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# Добавляем стиль, который скрывает experience-badge
css += """
/* Скрываем плашку 10+ лет, она перекрывает controls видео */
.about-image .experience-badge {
    display: none !important;
}
"""

# Обновляем версию
import re
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=5.2', html)
with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))

sftp.close()
ssh.close()
print("✅ Плашка '10+ лет в профессии' скрыта!")
