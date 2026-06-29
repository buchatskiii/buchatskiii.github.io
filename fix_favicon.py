#!/usr/bin/env python3
"""Fix favicon MIME type in Nginx and verify it works."""
import subprocess
import sys

PASSWORD = "qmc67Ra9TYas"
HOST = "139.100.234.22"

def run_ssh(command):
    """Run SSH command with password using sshpass."""
    cmd = f'sshpass -p "{PASSWORD}" ssh -o StrictHostKeyChecking=no root@{HOST} "{command}"'
    result = subprocess.run(
        ["C:\\Program Files\\Git\\bin\\bash.exe", "-c", cmd],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout + result.stderr

# 1. Check current Nginx config
print("=== Current Nginx config ===")
print(run_ssh("cat /etc/nginx/sites-enabled/default"))

# 2. Check if mime.types exists
print("\n=== Checking mime.types ===")
print(run_ssh("ls -la /etc/nginx/mime.types && head -5 /etc/nginx/mime.types"))

# 3. Check if favicon.png is served correctly
print("\n=== Checking favicon.png headers ===")
print(run_ssh("curl -s -I http://139.100.234.22/favicon.png | head -10"))

# 4. Check if favicon.ico is served correctly
print("\n=== Checking favicon.ico headers ===")
print(run_ssh("curl -s -I http://139.100.234.22/favicon.ico | head -10"))
