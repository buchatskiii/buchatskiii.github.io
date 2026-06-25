import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Проверяем порты
print("=== Слушающие порты ===")
stdin, stdout, stderr = ssh.exec_command("ss -tlnp")
print(stdout.read().decode())

# Проверяем фаервол
print("\n=== iptables ===")
stdin, stdout, stderr = ssh.exec_command("iptables -L -n 2>&1 | head -30")
print(stdout.read().decode())

# Проверяем ufw
print("\n=== ufw status ===")
stdin, stdout, stderr = ssh.exec_command("ufw status 2>&1")
print(stdout.read().decode())

# Проверяем nginx статус подробно
print("\n=== Nginx статус ===")
stdin, stdout, stderr = ssh.exec_command("systemctl status nginx --no-pager -l 2>&1")
print(stdout.read().decode())

# Проверяем все конфиги
print("\n=== Все конфиги в sites-enabled ===")
stdin, stdout, stderr = ssh.exec_command("ls -la /etc/nginx/sites-enabled/")
print(stdout.read().decode())

for conf in ['default', 'englishpro']:
    print(f"\n=== /etc/nginx/sites-enabled/{conf} ===")
    stdin, stdout, stderr = ssh.exec_command(f"cat /etc/nginx/sites-enabled/{conf} 2>&1")
    print(stdout.read().decode())

# Проверяем nginx.conf
print("\n=== /etc/nginx/nginx.conf (include) ===")
stdin, stdout, stderr = ssh.exec_command("grep include /etc/nginx/nginx.conf")
print(stdout.read().decode())

ssh.close()
