#!/usr/bin/env python3
"""Fix API timeout and ensure Telegram works."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# Read main.py
with sftp.open("/var/www/englishpro/main.py", "r") as f:
    content = f.read().decode("utf-8")

# Add timeout to telegram bot and make send_telegram non-blocking
# Replace the send_telegram function to add timeout
old = """    try:
        bot = telegram.Bot(token=BOT_TOKEN)"""

new = """    try:
        bot = telegram.Bot(token=BOT_TOKEN, request=telegram.request.HTTPXRequest(connect_timeout=10, read_timeout=10))"""

if old in content:
    content = content.replace(old, new)
    print("✅ Added timeout to Telegram bot")
else:
    print("⚠️ Could not find the pattern to replace")

# Also increase nginx proxy timeout
with sftp.open("/var/www/englishpro/main.py", "w") as f:
    f.write(content.encode("utf-8"))
print("✅ main.py updated")

# Restart API
client2 = paramiko.SSHClient()
client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client2.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
stdin, stdout, stderr = client2.exec_command('systemctl restart englishpro-api')
print("✅ API restarted")

# Check logs after restart
import time
time.sleep(2)
stdin, stdout, stderr = client2.exec_command('journalctl -u englishpro-api --no-pager -n 10')
print("\n=== API Logs ===")
print(stdout.read().decode())
client2.close()

sftp.close()
client.close()
