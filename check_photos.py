import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)
sftp = ssh.open_sftp()

# Проверяем файлы на сервере
print("=== Файлы в /var/www/englishpro/images/ ===")
try:
    files = sftp.listdir("/var/www/englishpro/images")
    for f in files:
        print(f"  {f}")
except Exception as e:
    print(f"  Ошибка: {e}")

# Проверяем права
print("\n=== Права на папку images ===")
stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/englishpro/images/")
print(stdout.read().decode())

# Проверяем HTML - какие ссылки на фото
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Ищем все src с /images/
import re
matches = re.findall(r'src="(/images/[^"]+)"', html)
print("\n=== Ссылки на /images/ в HTML ===")
for m in matches:
    print(f"  {m}")

# Проверяем конфиг nginx
print("\n=== Nginx config (секция location) ===")
stdin, stdout, stderr = ssh.exec_command("grep -A5 'location /images' /etc/nginx/sites-enabled/default")
print(stdout.read().decode() or "  Нет секции location /images")

# Проверяем корневую директорию nginx
print("\n=== root в nginx ===")
stdin, stdout, stderr = ssh.exec_command("grep 'root' /etc/nginx/sites-enabled/default")
print(stdout.read().decode())

sftp.close()
ssh.close()
