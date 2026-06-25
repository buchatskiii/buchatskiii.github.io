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

# Create directory
stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {remote_dir}")
print("mkdir:", stdout.read().decode(), stderr.read().decode())

sftp = ssh.open_sftp()

for f in files_to_upload:
    local_path = os.path.join(local_dir, f)
    remote_path = os.path.join(remote_dir, f)
    print(f"Uploading {f}...")
    sftp.put(local_path, remote_path)
    print(f"  OK")

sftp.close()

# Check nginx config
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-enabled/default")
config = stdout.read().decode()
print("\n=== Nginx config ===")
print(config)

# Check what's in conf.d
stdin, stdout, stderr = ssh.exec_command("ls -la /etc/nginx/conf.d/")
print("\n=== conf.d ===")
print(stdout.read().decode())

# Check sites-enabled
stdin, stdout, stderr = ssh.exec_command("ls -la /etc/nginx/sites-enabled/")
print("\n=== sites-enabled ===")
print(stdout.read().decode())

ssh.close()
print("\nDone!")
