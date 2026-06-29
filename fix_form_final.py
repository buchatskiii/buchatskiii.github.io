#!/usr/bin/env python3
"""Fix: ensure form works - check HTML form, fix API_URL, add .env."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# ===== 1. Read index.html and check form =====
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Find the form section
import re
form_match = re.search(r'<form[^>]*id="contactForm"[^>]*>.*?</form>', html, re.DOTALL)
if form_match:
    form_html = form_match.group()
    print("=== FORM HTML ===")
    print(form_html)
    
    # Check for privacy checkbox
    if 'privacy' in form_html:
        print("\n✅ Privacy checkbox found")
    else:
        print("\n❌ Privacy checkbox NOT found!")
    
    # Check for submit button
    if 'submit' in form_html or 'btn-submit' in form_html:
        print("✅ Submit button found")
    else:
        print("❌ Submit button NOT found!")
else:
    print("❌ Form not found!")

# ===== 2. Fix script.js - ensure API_URL is correct =====
with sftp.open("/var/www/englishpro/script.js", "r") as f:
    js = f.read().decode("utf-8")

# The API_URL is empty string, which means fetch goes to /api/lead on same domain
# This is correct! But let's verify
if "const API_URL = '';" in js or "const API_URL = ''" in js:
    print("\n✅ API_URL is empty (correct - same domain)")
else:
    print("\n⚠️ Fixing API_URL...")
    js = js.replace("const API_URL = '", "const API_URL = ''")
    # Make sure it's empty
    js = re.sub(r"const API_URL = '[^']*'", "const API_URL = ''", js)
    with sftp.open("/var/www/englishpro/script.js", "w") as f:
        f.write(js.encode("utf-8"))
    print("✅ API_URL set to empty string")

# ===== 3. Check .env file =====
try:
    with sftp.open("/var/www/englishpro/.env", "r") as f:
        env = f.read().decode("utf-8")
    print(f"\n=== .env ===")
    print(env)
except:
    print("\n❌ .env NOT FOUND on server!")
    # Check local .env
    try:
        with open("C:/Users/dlyav/Desktop/english-tutor/.env", "r") as f:
            local_env = f.read()
        print(f"\n=== Local .env ===")
        print(local_env)
        
        # Upload .env to server
        with sftp.open("/var/www/englishpro/.env", "w") as f:
            f.write(local_env.encode("utf-8"))
        print("✅ .env uploaded to server")
        
        # Restart API service
        client2 = paramiko.SSHClient()
        client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client2.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
        stdin, stdout, stderr = client2.exec_command('systemctl restart englishpro-api')
        print("✅ API service restarted")
        client2.close()
    except:
        print("❌ Local .env not found either!")

# ===== 4. Check API logs for errors =====
client2 = paramiko.SSHClient()
client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client2.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
stdin, stdout, stderr = client2.exec_command('journalctl -u englishpro-api --no-pager -n 30')
print("\n=== API Logs (last 30 lines) ===")
print(stdout.read().decode()[:2000])
client2.close()

sftp.close()
client.close()
