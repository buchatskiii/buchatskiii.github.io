import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

commands = [
    "ls -la /var/www/englishpro/",
    "cat /var/www/englishpro/index.html | head -5",
    "curl -s -D- http://localhost/ | head -20",
    "curl -s -D- http://localhost/index.html | head -20",
    "curl -s -D- http://139.100.234.22/ | head -20",
    "cat /var/log/nginx/error.log | tail -20",
]

for cmd in commands:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out[:500])
    if err: print("ERR:", err[:200])

ssh.close()
