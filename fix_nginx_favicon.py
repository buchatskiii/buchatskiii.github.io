#!/usr/bin/env python3
"""Fix Nginx config to serve favicon files with correct MIME types."""
import subprocess
import os

PASSWORD = "qmc67Ra9TYas"
HOST = "139.100.234.22"

def run_ssh(command):
    cmd = f'sshpass -p "{PASSWORD}" ssh -o StrictHostKeyChecking=no root@{HOST} "{command}"'
    result = subprocess.run(
        ["C:\\Program Files\\Git\\bin\\bash.exe", "-c", cmd],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout + result.stderr

# Read current nginx config
print("=== Current Nginx config ===")
config = run_ssh("cat /etc/nginx/sites-enabled/default")
print(config)

# Check if there's a try_files that catches everything
if "try_files" in config:
    print("\n=== Found try_files directive ===")
    # Extract the try_files line
    for line in config.split('\n'):
        if 'try_files' in line:
            print(f"  {line.strip()}")

# Check if favicon is being caught by a location block
print("\n=== Checking favicon access ===")
print(run_ssh("curl -s -o /dev/null -w '%{http_code} %{content_type}' http://139.100.234.22/favicon.ico"))
print()
print(run_ssh("curl -s -o /dev/null -w '%{http_code} %{content_type}' http://139.100.234.22/favicon.png"))
