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

# ===== 1. Переименовываем файлы на сервере =====
# student1.jpg -> 1.jpg и т.д.
# Но они уже 1.jpg, 2.jpg... Просто создадим симлинки
# Или проще - заменим ссылки в HTML

with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Заменяем все ссылки
replacements = {
    'images/student1.jpg': '/images/1.jpg',
    'images/student2.jpg': '/images/2.jpg',
    'images/student3.jpg': '/images/3.jpg',
    'images/student4.jpg': '/images/4.jpg',
    'images/student5.jpg': '/images/5.jpg',
    'images/student6.jpg': '/images/6.jpg',
}

for old, new in replacements.items():
    count = html.count(old)
    if count > 0:
        html = html.replace(old, new)
        print(f"✅ {old} -> {new} (x{count})")
    else:
        print(f"❌ {old} не найдено")

# Обновляем версию
html = re.sub(r'styles\.css\?v=[\d.]+', 'styles.css?v=25.0', html)
html = re.sub(r'script\.js\?v=[\d.]+', 'script.js?v=25.0', html)

with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("\n✅ HTML обновлён")

sftp.close()
ssh.close()

# Перезапускаем nginx
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(host, port, username, password)
ssh2.exec_command("systemctl restart nginx")
ssh2.close()

print("\n🎉 Готово! Фото должны отображаться")
