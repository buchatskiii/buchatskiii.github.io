#!/usr/bin/env python3
"""Final verification of video layout and sound."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

# Check the about-content structure
stdin, stdout, stderr = client.exec_command("sed -n '/about-content/,/about-text/p' /var/www/englishpro/index.html")
print("=== About content HTML ===")
print(stdout.read().decode())

# Check video tag
stdin, stdout, stderr = client.exec_command("grep 'about-video' /var/www/englishpro/index.html")
print("=== Video tag ===")
print(stdout.read().decode())

# Check video_fix.js
stdin, stdout, stderr = client.exec_command("cat /var/www/englishpro/video_fix.js")
print("=== video_fix.js ===")
print(stdout.read().decode())

# Check CSS about-content
stdin, stdout, stderr = client.exec_command("grep -A 10 'about-content {' /var/www/englishpro/styles.css | head -15")
print("=== CSS about-content ===")
print(stdout.read().decode())

client.close()
