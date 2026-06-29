#!/usr/bin/env python3
"""Deploy files to correct directory: /var/www/englishpro/"""
import paramiko
import os
import sys
import getpass

password = getpass.getpass("SSH password for root@139.100.234.22: ")

host = "139.100.234.22"
username = "root"

local_dir = r"C:\Users\dlyav\Desktop\english-tutor"
remote_dir = "/var/www/englishpro"

files = ["index.html", "styles.css"]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(host, 22, username, password, look_for_keys=False, allow_agent=False)
    print("Connected!")
    
    sftp = client.open_sftp()
    
    for filename in files:
        local_path = os.path.join(local_dir, filename)
        remote_path = os.path.join(remote_dir, filename)
        
        print(f"Uploading {filename} to {remote_path}...")
        sftp.put(local_path, remote_path)
        print(f"  OK")
    
    sftp.close()
    
    # Reload nginx
    stdin, stdout, stderr = client.exec_command("nginx -s reload")
    err = stderr.read().decode()
    if err:
        print(f"Nginx: {err}")
    else:
        print("Nginx reloaded OK")
    
    print("\nDone! Site updated at /var/www/englishpro/")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    client.close()
