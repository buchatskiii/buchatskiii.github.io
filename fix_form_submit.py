#!/usr/bin/env python3
"""Fix: check full script.js and fix form submission."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# Read full script.js
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

print("=== FULL script.js ===")
print(js)

# Read full main.py
with sftp.open("/var/www/englishpro/main.py", "r") as f:
    py = f.read().decode("utf-8")

print("\n\n=== FULL main.py ===")
print(py)

# Read .env
try:
    with sftp.open("/var/www/englishpro/.env", "r") as f:
        env = f.read().decode("utf-8")
    print("\n\n=== .env ===")
    print(env)
except:
    print("\n\n=== .env NOT FOUND ===")

sftp.close()
client.close()
