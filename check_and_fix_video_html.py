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

# Ищем about секцию
idx = html.find('about-content')
if idx >= 0:
    print("=== Секция about-content найдена ===")
    print(html[idx:idx+2000])
    print("...")
    print(html[idx+1500:idx+2500])

# Проверяем есть ли about-video
if 'about-video' in html:
    print("\n✅ about-video найден в HTML")
else:
    print("\n❌ about-video НЕ найден в HTML")
    # Ищем конец about-content
    end_idx = html.find('</div>', html.find('about-content'))
    print(f"\nКонтент вокруг about-content:")
    print(html[html.find('about-content'):html.find('about-content')+3000])

sftp.close()
ssh.close()
