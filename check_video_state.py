#!/usr/bin/env python3
"""Check current video state on server."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

# Find video files
stdin, stdout, stderr = client.exec_command("find /var/www/englishpro -name '*.mp4' -o -name '*.webm' -o -name '*.mov' 2>/dev/null")
print("=== Video files ===")
print(stdout.read().decode())

# Check about section
stdin, stdout, stderr = client.exec_command("grep -n -i 'about' /var/www/englishpro/index.html | head -20")
print("=== About section ===")
print(stdout.read().decode())

# Check for video/mp4 in HTML
stdin, stdout, stderr = client.exec_command("grep -n -i 'video\\|mp4\\|webm' /var/www/englishpro/index.html")
print("=== Video in HTML ===")
print(stdout.read().decode())

# Check about section full content
stdin, stdout, stderr = client.exec_command("sed -n '/about/,/results/p' /var/www/englishpro/index.html | head -60")
print("=== About section full ===")
print(stdout.read().decode())

client.close()
