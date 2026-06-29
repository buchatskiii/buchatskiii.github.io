#!/usr/bin/env python3
"""Execute a command on remote server via SSH with password."""
import paramiko
import sys
import os

host = "139.100.234.22"
port = 22
username = "root"
password = os.environ.get("SSH_PASSWORD", "")

if not password:
    print("ERROR: SSH_PASSWORD environment variable not set")
    sys.exit(1)

# Read the script to execute
script_path = r"C:\Users\dlyav\Desktop\english-tutor\fix_about_section.py"
with open(script_path, "r", encoding="utf-8") as f:
    script_content = f.read()

# Also copy the public key
pubkey_path = os.path.expanduser("~/.ssh/id_rsa.pub")
with open(pubkey_path, "r") as f:
    pubkey = f.read().strip()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(host, port, username, password, look_for_keys=False, allow_agent=False)
    print("Connected!")
    
    # First, install the public key for future passwordless access
    stdin, stdout, stderr = client.exec_command(
        f'mkdir -p ~/.ssh && echo "{pubkey}" >> ~/.ssh/authorized_keys && '
        f'sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys && '
        f'chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh && echo "KEY_INSTALLED"'
    )
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"STDERR: {err}")
    
    # Now upload and run the fix script
    stdin, stdout, stderr = client.exec_command(
        f'cat > /tmp/fix_about_section.py && python3 /tmp/fix_about_section.py'
    )
    stdin.write(script_content)
    stdin.flush()
    stdin.channel.shutdown_write()
    
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"STDERR: {err}")
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    client.close()
