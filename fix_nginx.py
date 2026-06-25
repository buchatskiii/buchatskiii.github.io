import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Check the nginx config
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-available/englishpro")
print("=== Nginx config ===")
print(stdout.read().decode())
print("ERR:", stderr.read().decode())

# Check files in www
stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/english-tutor/")
print("\n=== Files ===")
print(stdout.read().decode())

# Reload nginx
stdin, stdout, stderr = ssh.exec_command("nginx -t 2>&1 && nginx -s reload")
print("\n=== Nginx reload ===")
print(stdout.read().decode())
print(stderr.read().decode())

# Test
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost/")
print("\n=== HTTP test ===")
print(stdout.read().decode())

ssh.close()
