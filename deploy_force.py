#!/usr/bin/env python3
"""Force deploy - check and fix permissions, then upload."""
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
    
    # Fix permissions first
    stdin, stdout, stderr = client.exec_command(f"chmod 755 {remote_dir} && chmod 644 {remote_dir}/*.html {remote_dir}/*.css 2>/dev/null; echo 'PERMS_OK'")
    print("Permissions:", stdout.read().decode().strip())
    
    sftp = client.open_sftp()
    
    for filename in files:
        local_path = os.path.join(local_dir, filename)
        remote_path = os.path.join(remote_dir, filename)
        
        print(f"Uploading {filename}...")
        sftp.put(local_path, remote_path)
        # Force permissions
        sftp.chmod(remote_path, 0o644)
        print(f"  OK - {filename}")
    
    sftp.close()
    
    # Verify files
    stdin, stdout, stderr = client.exec_command(f"ls -la {remote_dir}/index.html {remote_dir}/styles.css && echo '---' && head -5 {remote_dir}/index.html")
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
    sys.exit(1)
finally:
    client.close()
