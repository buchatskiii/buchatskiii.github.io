import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

new_config = """server {
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

# Write via sftp
sftp = ssh.open_sftp()
with sftp.open("/etc/nginx/sites-available/englishpro", "w") as f:
    f.write(new_config)
sftp.close()

# Test and reload
stdin, stdout, stderr = ssh.exec_command("nginx -t 2>&1")
print("Test:", stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command("nginx -s reload")
print("Reload:", stdout.read().decode(), stderr.read().decode())

# Test
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost/")
print("HTTP test:", stdout.read().decode())

# Test via host header
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' -H 'Host: beklox.ru' http://localhost/")
print("HTTP test (beklox.ru):", stdout.read().decode())

ssh.close()
