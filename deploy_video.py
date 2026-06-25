import paramiko
import os

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

local_dir = r"C:\Users\dlyav\Desktop\english-tutor"
remote_dir = "/var/www/english-tutor"

files_to_upload = ["index.html", "styles.css", "script.js"]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

for f in files_to_upload:
    local_path = os.path.join(local_dir, f)
    remote_path = os.path.join(remote_dir, f)
    print(f"Uploading {f}...")
    sftp.put(local_path, remote_path)
    print(f"  OK")

sftp.close()
ssh.close()
print("\nDone! Files uploaded.")
