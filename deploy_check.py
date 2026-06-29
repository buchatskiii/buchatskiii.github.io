#!/usr/bin/env python3
"""Check what's on the server and deploy files."""
import paramiko
import os
import sys
import getpass

password = getpass.getpass("SSH password for root@139.100.234.22: ")

host = "139.100.234.22"
username = "root"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(host, 22, username, password, look_for_keys=False, allow_agent=False)
    
    # Check nginx config
    stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/default | grep -i root")
    print("=== Nginx root ===")
    print(stdout.read().decode())
    
    # Check what files are in html dir
    stdin, stdout, stderr = client.exec_command("ls -la /var/www/english-tutor/html/")
    print("=== Files in html dir ===")
    print(stdout.read().decode())
    
    # Check if there's another location
    stdin, stdout, stderr = client.exec_command("find /var/www -name 'index.html' 2>/dev/null")
    print("=== All index.html files ===")
    print(stdout.read().decode())
    
    # Check nginx config fully
    stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/default")
    print("=== Full nginx config ===")
    print(stdout.read().decode())
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
