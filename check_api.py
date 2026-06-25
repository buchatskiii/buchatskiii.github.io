import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Проверяем nginx конфиг
print("=== Nginx config ===")
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/default")
print(stdout.read().decode())

# Проверяем работает ли API
print("\n=== Проверка API через curl ===")
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs")
print(f"API docs: {stdout.read().decode()}")

# Проверяем запущен ли сервис
print("\n=== Статус API сервиса ===")
stdin, stdout, stderr = ssh.exec_command("systemctl status english-api --no-pager -l")
print(stdout.read().decode()[-500:])

# Проверяем лог ошибок nginx
print("\n=== Последние ошибки nginx ===")
stdin, stdout, stderr = ssh.exec_command("tail -20 /var/log/nginx/error.log")
print(stdout.read().decode())

ssh.close()
