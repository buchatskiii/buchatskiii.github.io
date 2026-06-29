#!/usr/bin/env python3
"""Clean up HTML: remove muted, fix extra divs, fix CSS conflicts."""
import paramiko
import re

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# Read current files
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# ===== 1. Fix HTML =====
# Remove 'muted' from video tag
html = html.replace('autoplay muted playsinline', 'autoplay playsinline')
print("✅ Removed 'muted' from video tag")

# Fix the extra closing divs in about-content
# Current broken structure:
# <div class="about-content">
#     <div class="about-video-wrapper">
#         <video>...</video>
#     </div>                    <- good
#     </div>                    <- extra! (was closing about-images)
#     </div>                    <- extra! (was closing about-images parent)
#     <div class="about-text">
# Need to remove the two extra </div> before about-text

# Find and fix the pattern
old_pattern = '''                    </div>
                    </div>
                </div>
                <div class="about-text">'''

new_pattern = '''                <div class="about-text">'''

if old_pattern in html:
    html = html.replace(old_pattern, new_pattern)
    print("✅ Fixed extra closing divs in about-content")
else:
    print("⚠️ Could not find exact pattern, trying alternative...")
    # Try with different indentation
    old_pattern2 = '''                    </div>
                    </div>
                </div>
                <div class="about-text">'''
    html = html.replace(old_pattern2, '\n                <div class="about-text">')
    print("✅ Fixed extra closing divs (alt)")

# ===== 2. Fix CSS conflicts =====
# The old .about-content at line 401 has display:flex with column direction
# The new one at line 1481 has display:flex with row direction
# We need to remove the old one and keep only the new one

# Find the old about-content CSS block (around line 401)
old_about_content_css = '''.about-content {
    display: flex;
    flex-direction: column;
    gap: 40px;
}

.about-content .about-image {
    flex: 1;
    min-width: 300px;
    max-width: 500px;
    position: relative;
}

.about-content .about-image img {
    width: 100%;
    height: auto;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
}

.about-content .about-text {
    flex: 1;
}'''

# Check if this exact block exists
if old_about_content_css in css:
    css = css.replace(old_about_content_css, '')
    print("✅ Removed old conflicting .about-content CSS")
else:
    print("⚠️ Could not find exact old about-content CSS, trying to remove by line range...")
    # Remove lines 401-415 (old about-content block)
    lines = css.split('\n')
    # Find the old .about-content block
    new_lines = []
    skip_block = False
    in_block = False
    brace_count = 0
    for line in lines:
        if '.about-content {' in line and 'about-content' in line and 'sticky' not in line and 'flex-direction' not in line:
            # Check if this is the OLD block (has flex-direction: column)
            if 'flex-direction' not in line:
                in_block = True
                brace_count = 0
                continue
        if in_block:
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
                in_block = False
            continue
        new_lines.append(line)
    css = '\n'.join(new_lines)
    print("✅ Removed old conflicting .about-content CSS (by brace matching)")

# Also remove the duplicate .about-content at line 1343 (mobile)
old_mobile_css = '''    .about-content {
        flex-direction: column;
        gap: 30px;
    }'''

if old_mobile_css in css:
    css = css.replace(old_mobile_css, '')
    print("✅ Removed old mobile .about-content CSS")

# Write files
with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ index.html saved")

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))
print("✅ styles.css saved")

sftp.close()
client.close()

# Reload nginx
client2 = paramiko.SSHClient()
client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client2.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
stdin, stdout, stderr = client2.exec_command('nginx -t && systemctl reload nginx')
print("✅ Nginx reloaded")
client2.close()

print("\n✅ All cleaned up!")
