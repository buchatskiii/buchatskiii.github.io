import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Check if git repo exists
stdin, stdout, stderr = ssh.exec_command("cd /var/www/englishpro && git status 2>&1")
print("=== Git status ===")
print(stdout.read().decode()[:500])
print(stderr.read().decode()[:500])

# Check git log
stdin, stdout, stderr = ssh.exec_command("cd /var/www/englishpro && git log --oneline -5 2>&1")
print("\n=== Git log ===")
print(stdout.read().decode()[:500])

# Check remote
stdin, stdout, stderr = ssh.exec_command("cd /var/www/englishpro && git remote -v 2>&1")
print("\n=== Git remote ===")
print(stdout.read().decode()[:500])

ssh.close()
