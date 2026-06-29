#!/usr/bin/env python3
"""Deploy the about section fix to the server."""
import paramiko
import os

host = "139.100.234.22"
port = 22
username = "root"
password = "Qwerty123!Qwerty123!"

local_dir = r"C:\Users\dlyav\Desktop\english-tutor"
remote_dir = "/var/www/english-tutor/html"

files_to_upload = ["index.html", "styles.css"]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port=port, username=username, password=password)
    print("Connected to server")
    
    sftp = ssh.open_sftp()
    
    for filename in files_to_upload:
        local_path = os.path.join(local_dir, filename)
        remote_path = os.path.join(remote_dir, filename)
        sftp.put(local_path, remote_path)
        print(f"Uploaded {filename}")
    
    sftp.close()
    
    # Reload nginx
    stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
    print("Nginx reloaded:", stdout.read().decode() + stderr.read().decode())
    
    print("Deploy complete!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
