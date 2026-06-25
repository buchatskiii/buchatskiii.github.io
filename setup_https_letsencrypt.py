import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Устанавливаем certbot
print("=== Установка certbot ===")
stdin, stdout, stderr = ssh.exec_command("apt-get update -qq && apt-get install -y -qq certbot python3-certbot-nginx 2>&1 | tail -5")
print(stdout.read().decode())

# Получаем сертификат
print("\n=== Получение SSL сертификата ===")
stdin, stdout, stderr = ssh.exec_command("certbot --nginx -d beklox.ru -d www.beklox.ru --non-interactive --agree-tos --email admin@beklox.ru 2>&1")
result = stdout.read().decode()
print(result)

# Проверяем
print("\n=== Проверка ===")
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' https://localhost/ -k 2>&1")
print(f"HTTPS ответ: {stdout.read().decode()}")

# Проверяем конфиг
print("\n=== Nginx config ===")
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/default")
print(stdout.read().decode())

ssh.close()
