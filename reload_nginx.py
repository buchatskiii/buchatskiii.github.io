import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
print("Done!")
