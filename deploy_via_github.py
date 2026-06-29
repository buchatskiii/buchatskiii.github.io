#!/usr/bin/env python3
"""Deploy files to server by pushing to GitHub and pulling on server."""
import paramiko
import os
import sys

host = "139.100.234.22"
port = 22
username = "root"
password = os.environ.get("SSH_PASSWORD", "")

if not password:
    print("ERROR: SSH_PASSWORD environment variable not set")
    sys.exit(1)

commands = [
    # Install git if not installed
    "which git || apt-get update && apt-get install -y git",
    
    # Clone or pull the repo
    "cd /var/www/english-tutor && if [ -d .git ]; then git pull; else git init && git remote add origin https://github.com/bexultan-english/english-tutor.git && git fetch origin && git checkout -b main origin/main; fi",
    
    # Copy files to html directory
    "cp -f /var/www/english-tutor/index.html /var/www/english-tutor/html/index.html",
    "cp -f /var/www/english-tutor/styles.css /var/www/english-tutor/html/styles.css",
    
    # Reload nginx
    "nginx -s reload",
    
    "echo 'DONE'"
]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(host, port, username, password, look_for_keys=False, allow_agent=False)
    print("Connected!")
    
    for cmd in commands:
        print(f"Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out:
            print(out)
        if err:
            print(f"STDERR: {err}")
    
    print("Deploy complete!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    client.close()
