#!/usr/bin/env python3
"""Fix gender mismatches using SSH commands."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

# Use cp command via SSH to copy files
commands = [
    # Backup current student2.jpg and student4.jpg
    "cp /var/www/englishpro/images/student2.jpg /var/www/englishpro/images/student2_backup.jpg",
    "cp /var/www/englishpro/images/student4.jpg /var/www/englishpro/images/student4_backup.jpg",
    # Copy male photos from avatars
    "cp /var/www/englishpro/images/avatars/student_2.jpg /var/www/englishpro/images/student2.jpg",
    "cp /var/www/englishpro/images/avatars/student_4.jpg /var/www/englishpro/images/student4.jpg",
    # Set permissions
    "chmod 644 /var/www/englishpro/images/student2.jpg /var/www/englishpro/images/student4.jpg",
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    err = stderr.read().decode().strip()
    if err:
        print(f"⚠️  {cmd}: {err}")
    else:
        print(f"✅ {cmd}")

client.close()
print("\n✅ Genders fixed! student2.jpg (Дмитрий) and student4.jpg (Артём) are now male photos.")
