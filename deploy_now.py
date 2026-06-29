#!/usr/bin/env python3
"""Deploy files to server. Usage: python deploy_now.py <password>"""
import paramiko
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python deploy_now.py <password>")
    print("Or: python deploy_now.py")
    print("Then type password and press Enter")
    sys.exit(1)

password = sys.argv[1]

host = "139.100.234.22"
port = 22
username = "root"

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
        print(f"  OK - {filename}")
    
    sftp.close()
    
    # Reload nginx
    stdin, stdout, stderr = client.exec_command("nginx -s reload")
    err = stderr.read().decode()
    if err:
        print(f"Nginx reload: {err}")
    else:
        print("Nginx reloaded OK")
    
    print("\nDone! Site updated.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    client.close()
