#!/usr/bin/env python3
"""Fix: remove autoplay, smaller video, replace name."""
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

# ===== 1. Replace "Анна Смирнова" with "Юсупов Бексултан Шукуралиевич" =====
html = html.replace("Анна Смирнова", "Юсупов Бексултан Шукуралиевич")
html = html.replace("Анна", "Бексултан")
html = html.replace("Anna", "Beksultan")
print("✅ Name replaced")

# ===== 2. Remove autoplay from video =====
html = html.replace('autoplay playsinline', 'playsinline')
print("✅ Removed autoplay from video")

# ===== 3. Remove IntersectionObserver JS (no autoplay on scroll) =====
# Replace video_fix.js with simple version (just set volume, no autoplay)
new_js = '''// ===== VIDEO: play only on user click, volume 33% =====
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;
    video.volume = 0.33;
    video.muted = false;
})();
'''

with sftp.open("/var/www/englishpro/video_fix.js", "w") as f:
    f.write(new_js.encode("utf-8"))
print("✅ video_fix.js updated: no autoplay, only on click")

# ===== 4. Make video smaller (30% instead of 50%) =====
# Remove old about-content CSS
css = re.sub(r'/\* ===== ABOUT SECTION: 50/50 LAYOUT ===== \*/', '', css)
css = re.sub(r'\.about-content\s*\{[^}]*\}', '', css)
css = re.sub(r'\.about-video-wrapper[^}]*\}', '', css)
css = re.sub(r'\.about-video[^}]*\}', '', css)
css = re.sub(r'\.about-text[^}]*\{[^}]*\}', '', css)
css = re.sub(r'\.about-video::-webkit-media-controls[^}]*\}', '', css)
css = re.sub(r'\.about-video::-webkit-media-controls-panel[^}]*\}', '', css)
css = re.sub(r'@media[^}]*\{[^}]*\.about-content[^}]*\}', '', css)
css = re.sub(r'@media[^}]*\{[^}]*\.about-video-wrapper[^}]*\}', '', css)

# Add new CSS with smaller video
new_css = '''
/* ===== ABOUT SECTION ===== */
.about-content {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 40px;
    width: 100%;
}

.about-video-wrapper {
    flex: 0 0 30%;
    max-width: 30%;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    background: #000;
}

.about-video {
    width: 100%;
    height: auto;
    display: block;
    aspect-ratio: 9/16;
    object-fit: cover;
    background: #1a1a2e;
    cursor: pointer;
}

.about-text {
    flex: 0 0 65%;
    max-width: 65%;
}

.about-video::-webkit-media-controls {
    background: rgba(0,0,0,0.3);
}

.about-video::-webkit-media-controls-panel {
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
}

@media (max-width: 768px) {
    .about-content {
        flex-direction: column;
        gap: 30px;
    }
    .about-video-wrapper {
        flex: 0 0 100%;
        max-width: 100%;
        width: 100%;
    }
    .about-text {
        flex: 0 0 100%;
        max-width: 100%;
    }
}
'''

css += new_css
print("✅ CSS updated: video 30%, text 65%")

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

print("\n✅ Done! Name changed, no autoplay, smaller video")
