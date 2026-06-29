#!/usr/bin/env python3
"""Fix: check and fix form submission API."""
import paramiko
import json

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# ===== 1. Check what files exist =====
files = sftp.listdir("/var/www/englishpro")
print("Files on server:")
for f in sorted(files):
    print(f"  {f}")

# ===== 2. Read main.py (API) =====
print("\n=== main.py ===")
try:
    with sftp.open("/var/www/englishpro/main.py", "r") as f:
        content = f.read().decode("utf-8")
        print(content[:2000])
except:
    print("main.py not found!")

# ===== 3. Read script.js =====
print("\n=== script.js ===")
try:
    with sftp.open("/var/www/englishpro/script.js", "r") as f:
        content = f.read().decode("utf-8")
        print(content[:2000])
except:
    print("script.js not found!")

# ===== 4. Read index.html form section =====
print("\n=== Form in index.html ===")
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Find form section
import re
form_match = re.search(r'<form[^>]*id="contactForm"[^>]*>.*?</form>', html, re.DOTALL)
if form_match:
    print(form_match.group()[:1500])
else:
    print("Form not found!")

# ===== 5. Check if API is running =====
stdin, stdout, stderr = client.exec_command('systemctl status englishpro-api 2>&1 || echo "no service"')
print("\n=== API Service ===")
print(stdout.read().decode()[:500])

# ===== 6. Check if port 8000 is listening =====
stdin, stdout, stderr = client.exec_command('ss -tlnp | grep 8000')
print("\n=== Port 8000 ===")
print(stdout.read().decode()[:500])

# ===== 7. Check nginx config for API proxy =====
stdin, stdout, stderr = client.exec_command('cat /etc/nginx/sites-enabled/englishpro 2>/dev/null || cat /etc/nginx/conf.d/englishpro.conf 2>/dev/null || cat /etc/nginx/sites-available/englishpro 2>/dev/null')
print("\n=== Nginx Config ===")
print(stdout.read().decode()[:2000])

sftp.close()
client.close()
