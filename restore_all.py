import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

# 1. Remove current directory and clone from GitHub
commands = [
    "rm -rf /var/www/englishpro",
    "git clone https://github.com/buchatskiii/english-tutor.git /var/www/englishpro",
    "ls -la /var/www/englishpro/",
]

for cmd in commands:
    print(f"\n=== {cmd} ===")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out[:500])
    if err: print("ERR:", err[:500])

# 2. Restore nginx config
nginx_config = """server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    root /var/www/englishpro;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /images/ {
        alias /var/www/englishpro/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    server_name beklox.ru www.beklox.ru;

    root /var/www/englishpro;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /images/ {
        alias /var/www/englishpro/images/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

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
    server_name beklox.ru www.beklox.ru;
    return 404;
}
"""

sftp = ssh.open_sftp()
with sftp.open("/etc/nginx/sites-available/englishpro", "w") as f:
    f.write(nginx_config)
sftp.close()
print("\n=== Nginx config written ===")

# 3. Test and reload
stdin, stdout, stderr = ssh.exec_command("nginx -t 2>&1")
print("Test:", stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
print("Reload:", stdout.read().decode(), stderr.read().decode())

# 4. Test
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost/")
print("HTTP test:", stdout.read().decode())

# 5. Check API
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost/api/health")
print("API health:", stdout.read().decode())

ssh.close()
print("\nDone!")
