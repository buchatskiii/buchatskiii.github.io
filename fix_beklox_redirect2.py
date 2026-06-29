#!/usr/bin/env python3
"""Fix beklox.ru redirect - change return 404 to return 301 https."""
import paramiko
import os

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

# Read the current config
stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/default")
config = stdout.read().decode()
print("Current config (last part):")
print(config[-500:])

# Fix: change return 404 to return 301 https://$host$request_uri
config = config.replace(
    "return 404; # managed by Certbot",
    "return 301 https://$host$request_uri; # managed by Certbot"
)

# Write to local temp file
local_path = "nginx_temp_fixed.conf"
with open(local_path, "w", encoding="utf-8") as f:
    f.write(config)

# Upload via sftp
sftp = client.open_sftp()
sftp.put(local_path, "/etc/nginx/sites-enabled/default")
sftp.close()

# Clean up local temp
os.remove(local_path)

# Test and reload
stdin, stdout, stderr = client.exec_command("nginx -t && systemctl reload nginx")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print(f"ERR: {err}")

# Verify
stdin, stdout, stderr = client.exec_command("curl -s -o /dev/null -w '%{http_code}' http://beklox.ru/")
print(f"HTTP beklox.ru status: {stdout.read().decode()}")

stdin, stdout, stderr = client.exec_command("curl -s -o /dev/null -w '%{http_code}' https://beklox.ru/")
print(f"HTTPS beklox.ru status: {stdout.read().decode()}")

client.close()
print("Done!")
