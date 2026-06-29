#!/usr/bin/env python3
"""Setup beklox.ru domain on the server."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

commands = [
    "cat /etc/nginx/sites-enabled/default 2>/dev/null || cat /etc/nginx/conf.d/default.conf 2>/dev/null || nginx -T 2>/dev/null | head -100",
    "cat /etc/nginx/nginx.conf | head -50",
    "ls -la /etc/nginx/sites-enabled/ 2>/dev/null",
    "ls -la /etc/nginx/conf.d/ 2>/dev/null",
    "host beklox.ru 2>/dev/null || nslookup beklox.ru 2>/dev/null || dig beklox.ru +short 2>/dev/null",
]

for cmd in commands:
    print(f"=== {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out)
    if err:
        print(f"ERR: {err}")
    print()

client.close()
