#!/usr/bin/env python3
"""Download photos from server and create an HTML page to view them."""
import paramiko
import os

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# Download all student photos
local_dir = r"C:\Users\dlyav\Desktop\english-tutor\photo_check"
os.makedirs(local_dir, exist_ok=True)

for i in range(1, 7):
    remote = f"/var/www/englishpro/images/student{i}.jpg"
    local = os.path.join(local_dir, f"student{i}.jpg")
    sftp.get(remote, local)
    print(f"Downloaded student{i}.jpg")

# Also download avatars
for i in range(1, 7):
    remote = f"/var/www/englishpro/images/avatars/student_{i}.jpg"
    local = os.path.join(local_dir, f"avatar_{i}.jpg")
    try:
        sftp.get(remote, local)
        print(f"Downloaded avatar_{i}.jpg")
    except:
        print(f"avatar_{i}.jpg not found")

sftp.close()
client.close()

# Create HTML to view them
html = """<!DOCTYPE html>
<html>
<head><title>Photo Check</title>
<style>
body { font-family: Arial; padding: 20px; }
h2 { margin-top: 30px; }
.grid { display: flex; flex-wrap: wrap; gap: 20px; }
.card { border: 1px solid #ddd; padding: 10px; border-radius: 8px; text-align: center; }
.card img { width: 200px; height: auto; display: block; margin-bottom: 8px; border-radius: 4px; }
</style>
</head>
<body>
<h1>Student Photos (current mapping)</h1>
<div class="grid">
"""
for i in range(1, 7):
    html += f"""
<div class="card">
    <img src="student{i}.jpg" alt="student{i}">
    <strong>student{i}.jpg</strong>
</div>"""

html += """</div>
<h1>Avatar Photos (original)</h1>
<div class="grid">
"""
for i in range(1, 7):
    html += f"""
<div class="card">
    <img src="avatar_{i}.jpg" alt="avatar_{i}">
    <strong>avatar_{i}.jpg</strong>
</div>"""

html += """
</div>
</body>
</html>"""

with open(os.path.join(local_dir, "index.html"), "w") as f:
    f.write(html)

print(f"\n✅ Created photo_check/index.html - open it in browser!")
