#!/usr/bin/env python3
"""Fix all issues: upload missing photos, fix about section, fix video."""
import paramiko
import os

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# === 1. Upload missing student photos ===
# Local files: 1.jpg-6.jpg in images/ folder
# Need to upload as student4.jpg, student5.jpg, student6.jpg
# Mapping from local files:
# 1.jpg -> student1.jpg (Екатерина - девушка) - already uploaded
# 2.jpg -> student2.jpg (Дмитрий - мужчина) - already uploaded
# 3.jpg -> student3.jpg (Алина - девушка) - already uploaded
# 4.jpg -> student4.jpg (Артём - мужчина) - MISSING
# 5.jpg -> student5.jpg (София - девушка) - MISSING
# 6.jpg -> student6.jpg (Мария - девушка) - MISSING

local_dir = r"C:\Users\dlyav\Desktop\english-tutor\images"
missing = [(4, "student4.jpg"), (5, "student5.jpg"), (6, "student6.jpg")]

for num, remote_name in missing:
    local_path = os.path.join(local_dir, f"{num}.jpg")
    remote_path = f"/var/www/englishpro/images/{remote_name}"
    if os.path.exists(local_path):
        sftp.put(local_path, remote_path)
        print(f"✅ Uploaded {local_path} -> {remote_path}")
    else:
        print(f"❌ Local file not found: {local_path}")

# Also upload teacher.jpg as teacher_about.jpg if needed
local_teacher = os.path.join(local_dir, "teacher.jpg")
if os.path.exists(local_teacher):
    sftp.put(local_teacher, "/var/www/englishpro/images/teacher_about.jpg")
    print(f"✅ Uploaded teacher.jpg -> teacher_about.jpg")

sftp.close()

# === 2. Fix permissions ===
stdin, stdout, stderr = client.exec_command("chmod 644 /var/www/englishpro/images/student*.jpg")
stdout.read()

# === 3. Read current index.html to fix ===
stdin, stdout, stderr = client.exec_command("cat /var/www/englishpro/index.html")
html = stdout.read().decode()

# === 4. Fix the about section - remove photo, keep only video with controls ===
# The current about section has a video with external URL. 
# We need to replace the entire about-content with just video + text

old_about = '''            <div class="about-content">
                <div class="about-video-wrapper">
                    <video id="aboutVideo" class="about-video" controls playsinline preload="metadata" poster="https://fs.oblakoteka.ru/c.videovssylku.ru/2026/06/26/POVELITEL-VSELENNOI.fr.jpeg" loop>
                        <source src="https://fs.oblakoteka.ru/c.videovssylku.ru/2026/06/26/POVELITEL-VSELENNOI.mp4" type="video/mp4">
                    </video>
                </div>
                <div class="about-text">'''

new_about = '''            <div class="about-content">
                <div class="about-video-wrapper">
                    <video id="aboutVideo" class="about-video" controls playsinline preload="metadata" poster="https://fs.oblakoteka.ru/c.videovssylku.ru/2026/06/26/POVELITEL-VSELENNOI.fr.jpeg">
                        <source src="https://fs.oblakoteka.ru/c.videovssylku.ru/2026/06/26/POVELITEL-VSELENNOI.mp4" type="video/mp4">
                    </video>
                </div>
                <div class="about-text">'''

if old_about in html:
    html = html.replace(old_about, new_about)
    print("✅ Removed 'loop' attribute from video")
else:
    print("⚠️ Could not find old about section to fix")

# === 5. Fix the about section - remove the photo badge "10 лет в профессии" ===
# Check if there's a photo with experience badge
old_photo_section = '''                <div class="about-image">
                    <img src="images/teacher_about.jpg" alt="Преподаватель английского">
                    <div class="experience-badge">
                        <span class="exp-years">10+</span>
                        <span class="exp-text">лет <br>в профессии</span>
                    </div>
                </div>
                <div class="about-text">'''

if old_photo_section in html:
    html = html.replace(old_photo_section, '''                <div class="about-text">''')
    print("✅ Removed photo with experience badge from about section")
else:
    print("⚠️ Photo section not found (may already be removed)")

# === 6. Write fixed HTML back ===
import tempfile
local_html = "index_fixed_temp.html"
with open(local_html, "w", encoding="utf-8") as f:
    f.write(html)

sftp2 = client.open_sftp()
sftp2.put(local_html, "/var/www/englishpro/index.html")
sftp2.close()
os.remove(local_html)
print("✅ Uploaded fixed index.html")

# === 7. Reload nginx ===
stdin, stdout, stderr = client.exec_command("nginx -t && systemctl reload nginx")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print(f"ERR: {err}")

# === 8. Verify ===
stdin, stdout, stderr = client.exec_command("ls -la /var/www/englishpro/images/student*.jpg")
print("Server photos:")
print(stdout.read().decode())

client.close()
print("\n✅ All fixes applied!")
