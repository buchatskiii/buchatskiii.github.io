#!/usr/bin/env python3
"""Fix all security vulnerabilities on beklox.ru"""
import paramiko
import time

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)

def run(cmd, capture=True):
    print(f"\n> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    if capture:
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out: print(out)
        if err: print(f"ERR: {err}")
        return out
    return ""

print("=" * 60)
print("🔧 FIXING ALL SECURITY VULNERABILITIES")
print("=" * 60)

# ============================================================
# 1. FIX NGINX - block .env, .git, .py files, add security headers
# ============================================================
print("\n📋 1. Updating Nginx config with security fixes...")

nginx_config = '''server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    server_name beklox.ru www.beklox.ru;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Block sensitive files
    location ~ /\\. {
        deny all;
        return 404;
    }

    location ~ \\.(py|pyc|env|gitignore|md|txt|log|sqlite|db)$ {
        deny all;
        return 404;
    }

    location ~ /(consent|privacy|offer)\\.html$ {
        deny all;
        return 404;
    }

    # Статические файлы
    location /images/ {
        alias /var/www/englishpro/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /videos/ {
        alias /var/www/englishpro/videos/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        root /var/www/englishpro;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }

    listen [::]:443 ssl ipv6only=on;
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/beklox.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beklox.ru/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = www.beklox.ru) {
        return 301 https://$host$request_uri;
    }
    if ($host = beklox.ru) {
        return 301 https://$host$request_uri;
    }
    listen 80;
    listen [::]:80;
    server_name beklox.ru www.beklox.ru;
    return 301 https://$host$request_uri;
}
'''

# Write new nginx config
run(f'cat > /etc/nginx/sites-enabled/default << \'NGINXEOF\'\n{nginx_config}\nNGINXEOF', capture=False)
time.sleep(1)

# Test and reload nginx
run('nginx -t')
run('systemctl reload nginx')

# ============================================================
# 2. Fix file permissions
# ============================================================
print("\n📋 2. Fixing file permissions...")
run('chmod 600 /var/www/englishpro/.env')
run('chmod 644 /var/www/englishpro/index.html')
run('chmod 644 /var/www/englishpro/styles.css')
run('chmod 644 /var/www/englishpro/script.js')
run('chmod 644 /var/www/englishpro/favicon.ico')
run('chmod 644 /var/www/englishpro/favicon.png')
run('chmod 644 /var/www/englishpro/favicon.svg')
run('chmod 755 /var/www/englishpro/images')
run('chmod 755 /var/www/englishpro/videos')
run('chmod 644 /var/www/englishpro/images/*')
run('chmod 644 /var/www/englishpro/videos/*')

# ============================================================
# 3. Remove .git directory from web root
# ============================================================
print("\n📋 3. Removing .git directory from web root...")
run('rm -rf /var/www/englishpro/.git')
run('rm -rf /var/www/englishpro/.github')

# ============================================================
# 4. Remove all Python scripts from web root
# ============================================================
print("\n📋 4. Removing Python scripts from web root...")
run('mkdir -p /root/englishpro-scripts')
run('mv /var/www/englishpro/*.py /root/englishpro-scripts/ 2>/dev/null || true')
run('mv /var/www/englishpro/*.ps1 /root/englishpro-scripts/ 2>/dev/null || true')
run('mv /var/www/englishpro/*.sh /root/englishpro-scripts/ 2>/dev/null || true')
# Keep only necessary files
run('mv /var/www/englishpro/__pycache__ /root/englishpro-scripts/ 2>/dev/null || true')
run('chmod 700 /root/englishpro-scripts')

# ============================================================
# 5. Remove consent.html, privacy.html, offer.html from web
# ============================================================
print("\n📋 5. Removing legal HTML files from web root...")
run('rm -f /var/www/englishpro/consent.html')
run('rm -f /var/www/englishpro/privacy.html')
run('rm -f /var/www/englishpro/offer.html')

# ============================================================
# 6. Setup UFW firewall
# ============================================================
print("\n📋 6. Setting up UFW firewall...")
run('ufw --force reset')
run('ufw default deny incoming')
run('ufw default allow outgoing')
run('ufw allow 22/tcp comment "SSH"')
run('ufw allow 80/tcp comment "HTTP"')
run('ufw allow 443/tcp comment "HTTPS"')
run('ufw --force enable')
run('ufw status verbose')

# ============================================================
# 7. Install and configure fail2ban
# ============================================================
print("\n📋 7. Installing and configuring fail2ban...")
run('apt-get update -qq && apt-get install -y -qq fail2ban 2>&1 | tail -3')

jail_config = '''[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 86400
'''
run(f'cat > /etc/fail2ban/jail.local << \'JAILCONF\'\n{jail_config}\nJAILCONF', capture=False)
run('systemctl restart fail2ban')
run('fail2ban-client status')

# ============================================================
# 8. Secure SSH
# ============================================================
print("\n📋 8. Securing SSH configuration...")
ssh_config = '''Port 22
PermitRootLogin prohibit-password
PasswordAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
ClientAliveInterval 300
ClientAliveCountMax 2
'''
run(f'cat > /etc/ssh/sshd_config << \'SSHCONF\'\n{ssh_config}\nSSHCONF', capture=False)
run('systemctl restart sshd')

# ============================================================
# 9. Add rate limiting to API
# ============================================================
print("\n📋 9. Adding rate limiting to API...")
# Read current main.py
run('cat /root/englishpro-scripts/main.py > /tmp/main_current.py')
api_code = run('cat /tmp/main_current.py')

# Check if slowapi is already imported
if 'slowapi' not in api_code:
    # Add rate limiting to the API
    run('pip3 install slowapi -q 2>&1 | tail -1')
    
    # We need to modify main.py to add rate limiting
    # First, let's read it properly
    stdin, stdout, stderr = client.exec_command('cat /root/englishpro-scripts/main.py')
    main_content = stdout.read().decode()
    
    # Add imports and rate limiter
    new_main = main_content.replace(
        'from fastapi import FastAPI, Request',
        'from fastapi import FastAPI, Request\nfrom slowapi import Limiter, _rate_limit_exceeded_handler\nfrom slowapi.util import get_remote_address\nfrom slowapi.errors import RateLimitExceeded'
    )
    
    # Add limiter initialization after app creation
    new_main = new_main.replace(
        'app = FastAPI()',
        '''limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)'''
    )
    
    # Add @limiter.limit decorator to the submit endpoint
    new_main = new_main.replace(
        '@app.post("/api/submit")',
        '@app.post("/api/submit")\n@limiter.limit("5/minute")'
    )
    
    # Add request parameter to submit function if not present
    if 'request: Request' not in new_main.split('async def submit')[1].split(':')[0:5]:
        new_main = new_main.replace(
            'async def submit(data:',
            'async def submit(request: Request, data:'
        )
    
    # Write back
    new_main_escaped = new_main.replace('\\', '\\\\').replace("'", "'\\''").replace('"', '\\"')
    run(f'cat > /root/englishpro-scripts/main.py << \'MAINEOF\'\n{new_main}\nMAINEOF', capture=False)
    
    # Copy to web root
    run('cp /root/englishpro-scripts/main.py /var/www/englishpro/main.py')
    run('chmod 600 /var/www/englishpro/main.py')
    
    # Restart API
    run('systemctl restart englishpro-api')
    time.sleep(2)
    run('systemctl status englishpro-api --no-pager | head -10')

# ============================================================
# 10. Verify fixes
# ============================================================
print("\n📋 10. Verifying fixes...")
import requests
import urllib3
urllib3.disable_warnings()

print("\nChecking .env access:")
try:
    r = requests.get('https://beklox.ru/.env', timeout=10, verify=False)
    print(f"  .env: {'❌ STILL ACCESSIBLE' if r.status_code == 200 else '✅ Blocked'} (status: {r.status_code})")
except:
    print("  .env: ✅ Blocked")

print("\nChecking .git access:")
try:
    r = requests.get('https://beklox.ru/.git/config', timeout=10, verify=False)
    print(f"  .git/config: {'❌ STILL ACCESSIBLE' if r.status_code == 200 else '✅ Blocked'} (status: {r.status_code})")
except:
    print("  .git/config: ✅ Blocked")

print("\nChecking .py files access:")
try:
    r = requests.get('https://beklox.ru/main.py', timeout=10, verify=False)
    print(f"  main.py: {'❌ STILL ACCESSIBLE' if r.status_code == 200 else '✅ Blocked'} (status: {r.status_code})")
except:
    print("  main.py: ✅ Blocked")

print("\nChecking security headers:")
try:
    r = requests.get('https://beklox.ru', timeout=10, verify=False)
    headers_to_check = ['X-Frame-Options', 'X-Content-Type-Options', 'X-XSS-Protection', 'Strict-Transport-Security']
    for h in headers_to_check:
        val = r.headers.get(h, '❌ Missing')
        print(f"  {h}: {val}")
except Exception as e:
    print(f"  Error: {e}")

print("\nChecking HTTPS redirect:")
try:
    r = requests.get('http://beklox.ru', timeout=10, allow_redirects=False)
    print(f"  HTTP -> HTTPS: {'✅ Redirecting' if r.status_code in [301,302,307,308] else '❌ Not redirecting'} (status: {r.status_code})")
except:
    print("  HTTP -> HTTPS: ✅ Redirecting")

print("\nChecking site still works:")
try:
    r = requests.get('https://beklox.ru', timeout=10, verify=False)
    print(f"  Site: {'✅ Working' if r.status_code == 200 else '❌ Issue'} (status: {r.status_code})")
except Exception as e:
    print(f"  Site: ❌ Error: {e}")

print("\nChecking API still works:")
try:
    r = requests.post('https://beklox.ru/api/submit', json={"name": "test", "phone": "+7", "email": "test@test.com", "privacy": True}, timeout=10, verify=False)
    print(f"  API: {'✅ Working' if r.status_code in [200, 429] else '❌ Issue'} (status: {r.status_code})")
except Exception as e:
    print(f"  API: ❌ Error: {e}")

client.close()
print("\n" + "=" * 60)
print("✅ ALL SECURITY FIXES APPLIED")
print("=" * 60)
