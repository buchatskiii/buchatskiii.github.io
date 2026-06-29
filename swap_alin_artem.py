#!/usr/bin/env python3
"""Swap photos: Алина (student3.jpg) <-> Артём (student4.jpg) in HTML."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# Read current HTML
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Swap student3.jpg and student4.jpg in HTML
html = html.replace('images/student3.jpg', 'images/TEMP_SWAP.jpg')
html = html.replace('images/student4.jpg', 'images/student3.jpg')
html = html.replace('images/TEMP_SWAP.jpg', 'images/student4.jpg')

# Write back
with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))

print("✅ HTML updated")

# Verify
stdin, stdout, stderr = client.exec_command("grep -B1 'student[34]\\.jpg' /var/www/englishpro/index.html")
print(stdout.read().decode())

sftp.close()
client.close()
print("\n✅ Swapped! Now Алина uses student4.jpg (4.jpg - девушка) and Артём uses student3.jpg (3.jpg - парень)")
