#!/usr/bin/env python3
"""Read server HTML, fix about section directly."""
import paramiko
import os

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

# Read current HTML
stdin, stdout, stderr = client.exec_command("cat /var/www/englishpro/index.html")
html = stdout.read().decode()

# Find the about section
import re

# Find the about-content div
match = re.search(r'<div class="about-content">(.*?)</div>\s+</div>\s+</section>', html, re.DOTALL)
if match:
    about_content = match.group(1)
    print("=== Current about-content ===")
    print(about_content[:500])
    print("...")
    
    # Check if there's a photo with experience badge
    if 'about-image' in about_content:
        print("\n⚠️ Found about-image (photo) - needs to be removed")
        # Remove the about-image div and keep only about-text
        # Pattern: <div class="about-image">...</div> followed by <div class="about-text">
        html = re.sub(
            r'<div class="about-image">.*?</div>\s*',
            '',
            html,
            flags=re.DOTALL
        )
        print("✅ Removed about-image div")
    
    # Check if video has 'loop' attribute
    if 'loop' in about_content and 'about-video' in about_content:
        html = html.replace(' loop>', '>')
        html = html.replace(' loop >', '>')
        print("✅ Removed 'loop' attribute from video")
    
    # Write back
    local_path = "index_fixed2.html"
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    sftp = client.open_sftp()
    sftp.put(local_path, "/var/www/englishpro/index.html")
    sftp.close()
    os.remove(local_path)
    print("✅ Uploaded fixed index.html")
else:
    print("❌ Could not find about-content section")
    # Print the section around "about" to debug
    idx = html.find('about-content')
    if idx > 0:
        print(html[idx-100:idx+500])

client.close()
