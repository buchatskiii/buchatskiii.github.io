import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

commands = [
    "ls -la /var/www/englishpro/videos/ 2>/dev/null || echo 'NO VIDEOS DIR'",
    "ls -la /var/www/englishpro/images/avatars/ 2>/dev/null || echo 'NO AVATARS DIR'",
    "grep -c 'aboutVideo' /var/www/englishpro/index.html",
    "grep -c 'aboutVideo' /var/www/englishpro/script.js",
    "grep 'aboutVideo' /var/www/englishpro/index.html | head -3",
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
