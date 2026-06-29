#!/usr/bin/env python3
"""Deploy updated favicon and CSS to server."""
import subprocess
import os

PASSWORD = "qmc67Ra9TYas"
HOST = "139.100.234.22"
BASE_DIR = r"C:\Users\dlyav\Desktop\english-tutor"

def run_ssh(command):
    """Run SSH command with password via plink or ssh."""
    # Try using ssh with sshpass-style input
    cmd = f'ssh -o StrictHostKeyChecking=no root@{HOST} "{command}"'
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = proc.communicate(input=PASSWORD + "\n")
    return stdout + stderr

def upload_file(local_path, remote_path):
    """Upload a file using scp with password."""
    cmd = f'scp -o StrictHostKeyChecking=no "{local_path}" root@{HOST}:{remote_path}'
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = proc.communicate(input=PASSWORD + "\n")
    return stdout + stderr

# Upload favicon.ico
print("Uploading favicon.ico...")
result = upload_file(
    os.path.join(BASE_DIR, "favicon.ico"),
    "/var/www/englishpro/favicon.ico"
)
print(result)

# Upload styles.css
print("Uploading styles.css...")
result = upload_file(
    os.path.join(BASE_DIR, "styles.css"),
    "/var/www/englishpro/styles.css"
)
print(result)

# Upload index.html
print("Uploading index.html...")
result = upload_file(
    os.path.join(BASE_DIR, "index.html"),
    "/var/www/englishpro/index.html"
)
print(result)

# Verify
print("\n=== Verifying ===")
result = run_ssh("curl -s -I http://139.100.234.22/favicon.ico | head -5")
print(result)
result = run_ssh("curl -s -I http://139.100.234.22/styles.css | head -5")
print(result)

print("\nDone!")
