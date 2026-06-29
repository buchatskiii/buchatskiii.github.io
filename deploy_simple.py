#!/usr/bin/env python3
"""Simple deploy: upload index.html and styles.css to server via SSH."""
import paramiko
import os
import sys

host = "139.100.234.22"
port = 22
username = "root"
password = os.environ.get("SSH_PASSWORD", "")

if not password:
    print("ERROR: SSH_PASSWORD environment variable not set")
    sys.exit(1)

local_dir = r"C:\Users\dlyav\Desktop\english-tutor"
remote_dir = "/var/www/english-tutor/html"

files = ["index.html", "styles.css"]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(host, port, username, password, look_for_keys=False, allow_agent=False)
    print("Connected to server!")
    
    sftp = client.open_sftp()
    
    for filename in files:
        local_path = os.path.join(local_dir, filename)
        remote_path = os.path.join(remote_dir, filename)
        
        print(f"Uploading {filename}...")
        sftp.put(local_path, remote_path)
        print(f"  ✅ {filename} uploaded")
    
    sftp.close()
    
    # Reload nginx
    stdin, stdout, stderr = client.exec_command("nginx -s reload")
    err = stderr.read().decode()
    if err:
        print(f"Nginx reload: {err}")
    else:
        print("✅ Nginx reloaded")
    
    print("\n✅ Deploy complete! Site updated.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    client.close()
