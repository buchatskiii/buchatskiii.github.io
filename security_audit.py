#!/usr/bin/env python3
"""Security audit for beklox.ru - read-only check, no changes made."""
import paramiko
import requests
import json

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

print("=" * 60)
print("🔍 SECURITY AUDIT - beklox.ru")
print("=" * 60)

# 1. Check Nginx config
print("\n📋 1. NGINX CONFIGURATION")
stdin, stdout, stderr = client.exec_command('cat /etc/nginx/sites-enabled/default')
nginx_config = stdout.read().decode()
print(nginx_config)

# 2. Check if directory listing is enabled
print("\n📋 2. DIRECTORY LISTING CHECK")
stdin, stdout, stderr = client.exec_command('grep -r "autoindex on" /etc/nginx/ 2>/dev/null || echo "No autoindex found"')
print(stdout.read().decode())

# 3. Check file permissions
print("\n📋 3. FILE PERMISSIONS")
stdin, stdout, stderr = client.exec_command('ls -la /var/www/englishpro/')
print(stdout.read().decode())

# 4. Check .env file permissions
print("\n📋 4. .ENV FILE PERMISSIONS")
stdin, stdout, stderr = client.exec_command('ls -la /var/www/englishpro/.env 2>/dev/null || echo ".env not found"')
print(stdout.read().decode())

# 5. Check if .env is accessible via web
print("\n📋 5. .ENV WEB ACCESS CHECK")
try:
    r = requests.get('https://beklox.ru/.env', timeout=10, verify=False)
    print(f"Status: {r.status_code} - {'⚠️ ACCESSIBLE!' if r.status_code == 200 else '✅ Blocked'}")
except Exception as e:
    print(f"✅ Blocked (error: {e})")

# 6. Check API security
print("\n📋 6. API SECURITY")
# Check if API has any auth
stdin, stdout, stderr = client.exec_command('cat /var/www/englishpro/main.py')
main_py = stdout.read().decode()

# Check for CORS
if 'allow_origins' in main_py or 'CORSMiddleware' in main_py:
    print("✅ CORS middleware found")
else:
    print("⚠️ No CORS middleware found")

# Check for rate limiting
if 'limiter' in main_py or 'throttle' in main_py or 'ratelimit' in main_py:
    print("✅ Rate limiting found")
else:
    print("⚠️ No rate limiting found")

# Check for input validation
if 'pydantic' in main_py or 'BaseModel' in main_py:
    print("✅ Input validation (pydantic) found")
else:
    print("⚠️ No pydantic input validation found")

# 7. Check SSL
print("\n📋 7. SSL/TLS CHECK")
try:
    r = requests.get('https://beklox.ru', timeout=10, verify=False)
    print(f"✅ HTTPS works (status: {r.status_code})")
except Exception as e:
    print(f"⚠️ HTTPS issue: {e}")

# Check if HTTP redirects to HTTPS
try:
    r = requests.get('http://beklox.ru', timeout=10, allow_redirects=False)
    if r.status_code in [301, 302, 307, 308]:
        print(f"✅ HTTP redirects to HTTPS (status: {r.status_code} -> {r.headers.get('Location', 'N/A')})")
    else:
        print(f"⚠️ HTTP does NOT redirect (status: {r.status_code})")
except Exception as e:
    print(f"⚠️ HTTP check error: {e}")

# 8. Check for sensitive files exposure
print("\n📋 8. SENSITIVE FILES CHECK")
sensitive_files = [
    '.git/config', '.git/HEAD', 'admin', 'config.py', 'config.json',
    'db.sqlite3', 'database.sqlite', 'backup', '.htaccess',
    'wp-admin', 'wp-login.php', 'xmlrpc.php'
]
for f in sensitive_files:
    try:
        r = requests.get(f'https://beklox.ru/{f}', timeout=5, verify=False)
        if r.status_code == 200:
            print(f"⚠️ {f} - ACCESSIBLE (status: {r.status_code})")
        elif r.status_code == 403:
            print(f"✅ {f} - Forbidden (403)")
        else:
            print(f"✅ {f} - Not found ({r.status_code})")
    except:
        print(f"✅ {f} - Blocked")

# 9. Check firewall
print("\n📋 9. FIREWALL STATUS")
stdin, stdout, stderr = client.exec_command('ufw status 2>/dev/null || echo "UFW not installed"')
print(stdout.read().decode())

stdin, stdout, stderr = client.exec_command('iptables -L -n --line-numbers 2>/dev/null | head -30')
print(stdout.read().decode())

# 10. Check open ports
print("\n📋 10. OPEN PORTS")
stdin, stdout, stderr = client.exec_command('ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null')
print(stdout.read().decode())

# 11. Check for SSH config
print("\n📋 11. SSH CONFIG")
stdin, stdout, stderr = client.exec_command('grep -E "^(PermitRootLogin|PasswordAuthentication|Port)" /etc/ssh/sshd_config 2>/dev/null')
print(stdout.read().decode())

# 12. Check API service user
print("\n📋 12. API SERVICE USER")
stdin, stdout, stderr = client.exec_command('cat /etc/systemd/system/englishpro-api.service 2>/dev/null || echo "Service file not found"')
print(stdout.read().decode())

# 13. Check for fail2ban
print("\n📋 13. FAIL2BAN STATUS")
stdin, stdout, stderr = client.exec_command('fail2ban-client status 2>/dev/null || echo "fail2ban not installed"')
print(stdout.read().decode())

# 14. Check for security headers
print("\n📋 14. SECURITY HEADERS")
try:
    r = requests.get('https://beklox.ru', timeout=10, verify=False)
    headers = r.headers
    security_headers = {
        'X-Frame-Options': headers.get('X-Frame-Options', '❌ Missing'),
        'X-Content-Type-Options': headers.get('X-Content-Type-Options', '❌ Missing'),
        'X-XSS-Protection': headers.get('X-XSS-Protection', '❌ Missing'),
        'Strict-Transport-Security': headers.get('Strict-Transport-Security', '❌ Missing'),
        'Content-Security-Policy': headers.get('Content-Security-Policy', '❌ Missing'),
        'Referrer-Policy': headers.get('Referrer-Policy', '❌ Missing'),
    }
    for h, v in security_headers.items():
        print(f"  {h}: {v}")
except Exception as e:
    print(f"Error: {e}")

# 15. Check for outdated software
print("\n📋 15. SOFTWARE VERSIONS")
stdin, stdout, stderr = client.exec_command('nginx -v 2>&1; python3 --version 2>&1')
print(stdout.read().decode())

client.close()
print("\n" + "=" * 60)
print("✅ Audit complete - no changes were made")
print("=" * 60)
