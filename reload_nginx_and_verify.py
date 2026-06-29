#!/usr/bin/env python3
"""Reload nginx and verify video changes."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

# Reload nginx
stdin, stdout, stderr = client.exec_command('nginx -t && systemctl reload nginx')
print("=== Nginx reload ===")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("Stderr:", err)

# Verify HTML
stdin, stdout, stderr = client.exec_command("grep -n 'autoplay\\|controls\\|video-hint\\|about-video' /var/www/englishpro/index.html")
print("=== HTML video section ===")
print(stdout.read().decode())

# Verify CSS
stdin, stdout, stderr = client.exec_command("grep -n 'about-video\\|video-hint\\|aspect-ratio' /var/www/englishpro/styles.css")
print("=== CSS video section ===")
print(stdout.read().decode())

# Verify JS
stdin, stdout, stderr = client.exec_command("head -20 /var/www/englishpro/video_fix.js")
print("=== video_fix.js (first 20 lines) ===")
print(stdout.read().decode())

client.close()
print("\n✅ Done! Check the site at https://beklox.ru/")
