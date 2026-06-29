#!/usr/bin/env python3
"""Fix: compact layout, remove patronymic from about."""
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

# ===== 1. Fix name in about section =====
# Replace "Юсупов Бексултан Шукуралиевич" with "Юсупов Бексултан" in the about heading
html = html.replace(
    'Привет! Меня зовут Юсупов Бексултан Шукуралиевич',
    'Привет! Меня зовут Юсупов Бексултан'
)
# Also fix any other occurrences
html = html.replace('Юсупов Бексултан Шукуралиевич', 'Юсупов Бексултан')
print("✅ Removed patronymic from about section")

# ===== 2. Make layout more compact =====
# Reduce section padding
css = css.replace('padding: 120px 0;', 'padding: 80px 0;')
css = css.replace('padding: 100px 0;', 'padding: 80px 0;')

# Reduce hero padding
css = css.replace('padding: 180px 0 100px;', 'padding: 140px 0 80px;')

# Reduce gaps in about-content
css = css.replace('gap: 40px;', 'gap: 30px;')

# Reduce about-video-wrapper size
css = css.replace('flex: 0 0 30%;', 'flex: 0 0 25%;')
css = css.replace('max-width: 30%;', 'max-width: 25%;')

# Increase text width
css = css.replace('flex: 0 0 65%;', 'flex: 0 0 70%;')
css = css.replace('max-width: 65%;', 'max-width: 70%;')

# Reduce font sizes in about-text h3
css = css.replace('font-size: 2.2rem;', 'font-size: 1.8rem;')

# Reduce achievement-item gap
css = css.replace('gap: 15px;', 'gap: 10px;')

# Reduce margin-bottom on about-text p
css = css.replace('margin-bottom: 20px;', 'margin-bottom: 15px;')

# Reduce section header margin
css = css.replace('margin-bottom: 60px;', 'margin-bottom: 40px;')

# Reduce hero-content gap
css = css.replace('gap: 60px;', 'gap: 40px;')

# Reduce hero stats gap
css = css.replace('gap: 50px;', 'gap: 30px;')

# Reduce result card padding
css = css.replace('padding: 30px;', 'padding: 24px;')

# Reduce pricing card padding
css = css.replace('padding: 40px;', 'padding: 30px;')

# Reduce timeline item padding
css = css.replace('padding: 30px;', 'padding: 24px;')

# Reduce cert card padding
css = css.replace('padding: 30px;', 'padding: 24px;')

# Reduce testimonial card padding
css = css.replace('padding: 35px;', 'padding: 28px;')

# Reduce contact form padding
css = css.replace('padding: 40px;', 'padding: 30px;')

# Reduce nav links gap
css = css.replace('gap: 35px;', 'gap: 25px;')

# Reduce hero title font
css = css.replace('font-size: 3.5rem;', 'font-size: 2.8rem;')

# Reduce hero subtitle font
css = css.replace('font-size: 1.2rem;', 'font-size: 1rem;')

# Reduce section title font
css = css.replace('font-size: 2.8rem;', 'font-size: 2.2rem;')

# Reduce section subtitle font
css = css.replace('font-size: 1.15rem;', 'font-size: 1rem;')

# Reduce pricing price font
css = css.replace('font-size: 3rem;', 'font-size: 2.5rem;')

# Reduce result score font
css = css.replace('font-size: 3rem;', 'font-size: 2.5rem;')

# Reduce stat number font
css = css.replace('font-size: 2.8rem;', 'font-size: 2.2rem;')

# Reduce timeline number font
css = css.replace('font-size: 3rem;', 'font-size: 2.5rem;')

# Reduce faq question font
css = css.replace('font-size: 1.15rem;', 'font-size: 1rem;')

# Reduce footer padding
css = css.replace('padding: 60px 0 30px;', 'padding: 40px 0 20px;')

print("✅ Layout made more compact")

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

print("\n✅ Done! Compact layout, no patronymic")
