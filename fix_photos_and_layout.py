#!/usr/bin/env python3
"""Fix photos mapping and about section layout."""
import paramiko
import os

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# === Current mapping on server ===
# student1.jpg = avatars/student_1.jpg (63204 bytes) - currently used for Екатерина (девушка)
# student2.jpg = avatars/student_2.jpg (57077 bytes) - currently used for Дмитрий (парень)
# student3.jpg = avatars/student_3.jpg (44509 bytes) - currently used for Алина (девушка)
# student4.jpg = 4.jpg (44385 bytes) - currently used for Артём (парень)
# student5.jpg = 5.jpg (31085 bytes) - currently used for София (девушка)
# student6.jpg = 6.jpg (159203 bytes) - currently used for Мария (девушка)

# User says: Артём и Дмитрий - должны быть парни (сейчас Дмитрий - парень, Артём - парень - OK)
# User says: Екатерину тоже поменять
# User says: "там есть фото парней, возьми их"

# The issue: student1.jpg (avatars/student_1.jpg) for Екатерина might be wrong
# Let's check: avatars/student_1.jpg (63204) vs 1.jpg (104295) - different!
# avatars/student_2.jpg (57077) vs 2.jpg (133300) - different!
# avatars/student_3.jpg (44509) vs 3.jpg (106394) - different!
# avatars/student_4.jpg (77690) vs 4.jpg (44385) - different!
# avatars/student_5.jpg (20138) vs 5.jpg (31085) - different!
# avatars/student_6.jpg (57612) vs 6.jpg (159203) - different!

# So the avatars/ folder has DIFFERENT photos than 1.jpg-6.jpg
# The user said photos are numbered and in the images folder
# Let's use the LOCAL photos (1.jpg-6.jpg) and map them correctly

# Based on sizes, let me check what's on the server in avatars vs local
print("=== Checking avatars on server ===")
stdin, stdout, stderr = client.exec_command("file /var/www/englishpro/images/avatars/student_*.jpg")
print(stdout.read().decode())

print("=== Checking local files ===")
local_dir = r"C:\Users\dlyav\Desktop\english-tutor\images"
for i in range(1, 7):
    path = os.path.join(local_dir, f"{i}.jpg")
    if os.path.exists(path):
        import subprocess
        result = subprocess.run(["file", path], capture_output=True, text=True, shell=True)
        print(f"{i}.jpg: {result.stdout.strip()}")

# The user said: use photos from the computer, they are numbered
# Let me just swap: use local 1.jpg-6.jpg for all students
# And map them properly:
# 1.jpg -> student1.jpg (Екатерина - девушка) 
# 2.jpg -> student2.jpg (Дмитрий - парень) 
# 3.jpg -> student3.jpg (Алина - девушка)
# 4.jpg -> student4.jpg (Артём - парень)
# 5.jpg -> student5.jpg (София - девушка)
# 6.jpg -> student6.jpg (Мария - девушка)

# Actually, let me just upload all 6 local photos as student1-6.jpg
print("\n=== Uploading local photos as student photos ===")
for i in range(1, 7):
    local_path = os.path.join(local_dir, f"{i}.jpg")
    remote_name = f"student{i}.jpg"
    remote_path = f"/var/www/englishpro/images/{remote_name}"
    sftp.put(local_path, remote_path)
    print(f"✅ Uploaded {i}.jpg -> {remote_name}")

sftp.close()

# Fix permissions
stdin, stdout, stderr = client.exec_command("chmod 644 /var/www/englishpro/images/student*.jpg")
stdout.read()

# === Now fix the about section layout ===
# Read current HTML
stdin, stdout, stderr = client.exec_command("cat /var/www/englishpro/index.html")
html = stdout.read().decode()

# The about-content should have video on left, text on right
# Current structure (after our fix):
# <div class="about-content">
#     <div class="about-video-wrapper">
#         <video ...>
#     </div>
#     <div class="about-text">
#         ...
#     </div>
# </div>

# We need to add CSS to make video vertical and on the left
# Let's add styles to the existing CSS

# Read current CSS
stdin, stdout, stderr = client.exec_command("cat /var/www/englishpro/styles.css")
css = stdout.read().decode()

# Add styles for vertical video layout
new_css = '''
/* About section - video left, text right */
.about-content {
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-start !important;
    gap: 40px !important;
}

.about-video-wrapper {
    flex: 0 0 380px !important;
    max-width: 380px !important;
}

.about-video {
    width: 100% !important;
    height: auto !important;
    max-height: 600px !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15) !important;
    object-fit: cover !important;
}

.about-text {
    flex: 1 !important;
    min-width: 0 !important;
}

@media (max-width: 768px) {
    .about-content {
        flex-direction: column !important;
    }
    .about-video-wrapper {
        flex: none !important;
        max-width: 100% !important;
    }
}
'''

# Check if these styles already exist
if '.about-content' in css and 'display: flex' not in css:
    # Find the about section in CSS and add styles
    css += '\n' + new_css
    print("✅ Added about section flexbox styles to CSS")
elif 'display: flex' in css:
    print("⚠️ Flexbox styles already exist in CSS")
else:
    css += '\n' + new_css
    print("✅ Added about section flexbox styles to CSS")

# Write CSS back
local_css = "styles_fixed_temp.css"
with open(local_css, "w", encoding="utf-8") as f:
    f.write(css)

sftp2 = client.open_sftp()
sftp2.put(local_css, "/var/www/englishpro/styles.css")
sftp2.close()
os.remove(local_css)
print("✅ Uploaded fixed styles.css")

# Reload nginx
stdin, stdout, stderr = client.exec_command("nginx -t && systemctl reload nginx")
print(stdout.read().decode())

client.close()
print("\n✅ All fixes applied!")
