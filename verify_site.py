import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

commands = [
    "curl -s http://localhost/ | head -3",
    "curl -s -o /dev/null -w '%%{http_code}' http://localhost/styles.css",
    "curl -s -o /dev/null -w '%%{http_code}' http://localhost/script.js",
    "curl -s -o /dev/null -w '%%{http_code}' http://localhost/api/lead -X POST -H 'Content-Type: application/json' -d '{\"test\":1}'",
    "curl -s http://localhost/api/health 2>/dev/null || echo 'no health endpoint'",
    "cat /var/log/nginx/access.log | tail -5",
]

for cmd in commands:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out[:300])
    if err: print("ERR:", err[:200])

ssh.close()
