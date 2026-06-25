import paramiko
import socket

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

# Проверяем DNS
print("=== DNS проверка ===")
try:
    ip = socket.gethostbyname("beklox.ru")
    print(f"beklox.ru -> {ip}")
except Exception as e:
    print(f"❌ DNS ошибка: {e}")

try:
    ip = socket.gethostbyname("www.beklox.ru")
    print(f"www.beklox.ru -> {ip}")
except Exception as e:
    print(f"❌ www DNS ошибка: {e}")

# Проверяем доступность порта 80
print("\n=== Проверка порта 80 ===")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
result = sock.connect_ex(('139.100.234.22', 80))
if result == 0:
    print("✅ Порт 80 открыт")
else:
    print(f"❌ Порт 80 закрыт (код: {result})")
sock.close()

# Проверяем порт 443
print("\n=== Проверка порта 443 ===")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
result = sock.connect_ex(('139.100.234.22', 443))
if result == 0:
    print("✅ Порт 443 открыт")
else:
    print(f"❌ Порт 443 закрыт (код: {result})")
sock.close()

# Проверяем на сервере
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

print("\n=== Проверка на сервере ===")
stdin, stdout, stderr = ssh.exec_command("curl -s -I http://localhost/ 2>&1 | head -10")
print(stdout.read().decode())

# Проверяем hosts
print("\n=== /etc/hosts ===")
stdin, stdout, stderr = ssh.exec_command("cat /etc/hosts")
print(stdout.read().decode())

# Проверяем DNS резолв на сервере
print("\n=== DNS на сервере ===")
stdin, stdout, stderr = ssh.exec_command("nslookup beklox.ru 2>&1 || host beklox.ru 2>&1 || dig beklox.ru 2>&1")
print(stdout.read().decode())

ssh.close()
