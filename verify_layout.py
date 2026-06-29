#!/usr/bin/env python3
"""Verify the video layout changes."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

# Check about-content structure
stdin, stdout, stderr = client.exec_command("sed -n '/about-content/,/about-text/p' /var/www/englishpro/index.html | head -20")
print("=== About content HTML ===")
print(stdout.read().decode())

# Check video tag
stdin, stdout, stderr = client.exec_command("grep -n 'about-video\\|autoplay\\|muted\\|volume' /var/www/englishpro/index.html /var/www/englishpro/video_fix.js 2>/dev/null")
print("=== Video attributes ===")
print(stdout.read().decode())

# Check CSS
stdin, stdout, stderr = client.exec_command("grep -n 'about-content\\|about-video-wrapper\\|about-text\\|sticky' /var/www/englishpro/styles.css")
print("=== CSS layout ===")
print(stdout.read().decode())

client.close()
