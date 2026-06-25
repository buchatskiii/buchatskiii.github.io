import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Проверяем nginx
print("=== Nginx статус ===")
stdin, stdout, stderr = ssh.exec_command("systemctl status nginx --no-pager -l 2>&1 | head -20")
print(stdout.read().decode())

print("\n=== Nginx config ===")
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/default")
print(stdout.read().decode())

print("\n=== Nginx test ===")
stdin, stdout, stderr = ssh.exec_command("nginx -t 2>&1")
print(stdout.read().decode())

print("\n=== Файлы в /var/www/englishpro/ ===")
stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/englishpro/")
print(stdout.read().decode())

print("\n=== Проверка порта 80 ===")
stdin, stdout, stderr = ssh.exec_command("ss -tlnp | grep 80")
print(stdout.read().decode())

ssh.close()
