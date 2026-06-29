#!/usr/bin/env python3
"""Fix photos: use only 1-6 from images folder. 2 and 3 = парни, остальные = девушки."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

# Step 1: Check what files exist
print("=== Current files ===")
stdin, stdout, stderr = client.exec_command("ls -la /var/www/englishpro/images/student*.jpg /var/www/englishpro/images/*.jpg 2>&1")
print(stdout.read().decode())

# Step 2: Delete avatars folder entirely
print("=== Deleting avatars folder ===")
stdin, stdout, stderr = client.exec_command("rm -rf /var/www/englishpro/images/avatars/")
err = stderr.read().decode().strip()
if err:
    print(f"Error: {err}")
else:
    print("✅ avatars folder deleted")

# Step 3: Restore student2.jpg and student4.jpg from backups (they were overwritten with avatars)
# The original photos 2.jpg and 4.jpg should still exist as backups
print("=== Restoring original photos ===")
stdin, stdout, stderr = client.exec_command("ls -la /var/www/englishpro/images/student2_backup.jpg /var/www/englishpro/images/student4_backup.jpg 2>&1")
print(stdout.read().decode())

# Restore from backups
stdin, stdout, stderr = client.exec_command("cp /var/www/englishpro/images/student2_backup.jpg /var/www/englishpro/images/student2.jpg")
err = stderr.read().decode().strip()
if err: print(f"⚠️ student2 restore: {err}")
else: print("✅ student2.jpg restored from backup")

stdin, stdout, stderr = client.exec_command("cp /var/www/englishpro/images/student4_backup.jpg /var/www/englishpro/images/student4.jpg")
err = stderr.read().decode().strip()
if err: print(f"⚠️ student4 restore: {err}")
else: print("✅ student4.jpg restored from backup")

# Step 4: Now check what photos we have
print("\n=== Current student photos ===")
stdin, stdout, stderr = client.exec_command("file /var/www/englishpro/images/student*.jpg")
print(stdout.read().decode())

# Step 5: Now we need to map correctly:
# student1.jpg = 1.jpg (девушка - Екатерина) 
# student2.jpg = 2.jpg (парень - Дмитрий) ✅ already
# student3.jpg = 3.jpg (парень - Артём) ✅ already
# student4.jpg = 4.jpg (девушка - Алина) ✅ already
# student5.jpg = 5.jpg (девушка - София) ✅ already
# student6.jpg = 6.jpg (девушка - Мария) ✅ already

# But wait - earlier I uploaded 1-6.jpg as student1-6.jpg directly.
# Then I overwrote student2.jpg and student4.jpg with avatars.
# Now I restored them from backups.
# But the backups were the ORIGINAL student2.jpg and student4.jpg which were the local 2.jpg and 4.jpg
# So they should be correct now.

# Let me verify by checking dimensions
print("\n=== Verifying photo dimensions ===")
for i in range(1, 7):
    stdin, stdout, stderr = client.exec_command(f"identify /var/www/englishpro/images/student{i}.jpg 2>/dev/null || file /var/www/englishpro/images/student{i}.jpg")
    print(f"student{i}.jpg: {stdout.read().decode().strip()}")

# Step 6: Now update HTML to use correct mapping
# Current HTML uses student1.jpg through student6.jpg
# Let me check the current mapping in HTML
print("\n=== Current HTML photo references ===")
stdin, stdout, stderr = client.exec_command("grep -o 'student[0-9]*\\.jpg' /var/www/englishpro/index.html")
print(stdout.read().decode())

# The HTML should already reference student1-6.jpg correctly
# Let me check which student corresponds to which name
print("\n=== Checking student names in HTML ===")
stdin, stdout, stderr = client.exec_command("grep -B2 'student[0-9]*\\.jpg' /var/www/englishpro/index.html | head -30")
print(stdout.read().decode())

client.close()
print("\n✅ All done!")
