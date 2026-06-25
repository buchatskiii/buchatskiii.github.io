import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

commands = [
    "systemctl restart english-tutor 2>&1 || echo 'no service'",
    "systemctl status english-tutor 2>&1 | head -10",
    "curl -s http://localhost/api/health",
    "curl -s -o /dev/null -w '%{http_code}' http://localhost/",
]

for cmd in commands:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out[:500])
    if err: print("ERR:", err[:200])

ssh.close()
