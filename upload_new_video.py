import paramiko
import os

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

local_path = r"C:\Users\dlyav\Desktop\english-tutor\videos\повелитель вселенной.MP4"
remote_path = "/var/www/englishpro/videos/povelitel_vselennoy.mp4"

file_size = os.path.getsize(local_path)
print(f"Размер файла: {file_size / 1024 / 1024:.2f} MB")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

# Загружаем файл
print("Загрузка на сервер...")
sftp.put(local_path, remote_path)
print("✅ Видео загружено!")

# Проверяем
with sftp.open(remote_path, "rb") as f:
    f.seek(0, 2)
    remote_size = f.tell()
    print(f"Размер на сервере: {remote_size / 1024 / 1024:.2f} MB")

sftp.close()
ssh.close()
print("\n✅ Готово! Видео обновлено на сервере.")
