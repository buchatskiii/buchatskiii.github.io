import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

# Читаем HTML
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Ищем строку с video
import re
matches = re.findall(r'<video[^>]*>', html)
print("=== VIDEO TAGS IN HTML ===")
for m in matches:
    print(m)

# Ищем aboutVideo
if 'aboutVideo' in html:
    print("\n✅ aboutVideo найден в HTML")
else:
    print("\n❌ aboutVideo НЕ найден в HTML!")

# Читаем JS
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

print("\n=== VIDEO JS BLOCK ===")
# Находим блок про video
start = js.find('// ===== Video in About section')
if start >= 0:
    end = js.find('// Show button again when video ends', start)
    if end < 0:
        end = js.find('// =====', start + 10)
    if end < 0:
        end = start + 2000
    print(js[start:end])
else:
    print("❌ Блок Video in About section НЕ найден!")
    # Ищем любые упоминания aboutVideo
    if 'aboutVideo' in js:
        idx = js.find('aboutVideo')
        print(f"  Но aboutVideo найден на позиции {idx}")
        print(js[max(0,idx-200):idx+500])

sftp.close()
ssh.close()
