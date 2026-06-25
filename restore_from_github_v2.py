import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# Откатываем через git
commands = [
    "cd /var/www/englishpro && git reset --hard HEAD",
    "cd /var/www/englishpro && git clean -fd",
    "cd /var/www/englishpro && git pull origin main",
    "systemctl restart nginx",
    "systemctl restart english-api",
]

for cmd in commands:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"$ {cmd}")
    if out: print(out)
    if err: print(f"ERR: {err}")
    print()

ssh.close()
print("✅ Откат из GitHub выполнен!")
