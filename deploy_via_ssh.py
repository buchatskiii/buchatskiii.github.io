#!/usr/bin/env python3
"""Deploy files via SSH pipe (cat) to force overwrite."""
import paramiko
import os
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
    
    for filename in files:
        local_path = os.path.join(local_dir, filename)
        remote_path = os.path.join(remote_dir, filename)
        
        # Read local file
        with open(local_path, 'rb') as f:
            content = f.read()
        
        print(f"Uploading {filename} ({len(content)} bytes)...")
        
        # Use SFTP with explicit overwrite
        sftp = client.open_sftp()
        with sftp.open(remote_path, 'wb') as f:
            f.write(content)
        sftp.close()
        
        # Set permissions
        stdin, stdout, stderr = client.exec_command(f"chmod 644 {remote_path}")
        print(f"  OK - {filename}")
    
    # Verify
    stdin, stdout, stderr = client.exec_command(f"wc -c /var/www/englishpro/index.html && grep -c 'about-image' /var/www/englishpro/index.html")
    print("=== Verification ===")
    print(stdout.read().decode())
    
    # Reload nginx
    stdin, stdout, stderr = client.exec_command("nginx -s reload")
    err = stderr.read().decode()
    if err:
        print(f"Nginx: {err}")
    else:
        print("Nginx reloaded OK")
    
    print("\nDone!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
