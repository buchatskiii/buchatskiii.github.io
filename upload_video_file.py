import paramiko
import os

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

# Укажите путь к вашему видеофайлу
video_file = r"C:\Users\dlyav\Desktop\english-tutor\videos\presentation.mp4"

if not os.path.exists(video_file):
    print(f"❌ Файл не найден: {video_file}")
    print()
    print("📌 Положите ваш MP4 файл в папку:")
    print("   C:\\Users\\dlyav\\Desktop\\english-tutor\\videos\\")
    print("   и назовите его presentation.mp4")
    print()
    print("   Или измените переменную video_file в этом скрипте")
    exit(1)

remote_path = f"/var/www/englishpro/videos/{os.path.basename(video_file)}"
file_size = os.path.getsize(video_file)
file_size_mb = file_size / (1024 * 1024)

print(f"📹 Загружаю видео: {os.path.basename(video_file)}")
print(f"📦 Размер: {file_size_mb:.1f} MB")
print(f"⏳ Это может занять некоторое время...")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()
sftp.put(video_file, remote_path)
sftp.close()
ssh.close()

print(f"✅ Видео успешно загружено!")
print(f"🌐 URL: http://139.100.234.22/videos/{os.path.basename(video_file)}")
print()
print("📝 HTML-код для вставки на сайт:")
print("=" * 60)
print('<div class="video-container">')
print('  <video width="100%" controls poster="/images/video-poster.jpg">')
print(f'    <source src="/videos/{os.path.basename(video_file)}" type="video/mp4">')
print('    Ваш браузер не поддерживает видео.')
print('  </video>')
print('</div>')
print("=" * 60)
