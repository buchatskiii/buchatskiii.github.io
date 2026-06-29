#!/usr/bin/env python3
"""Send command to server to pull from GitHub and update files."""
import requests
import json

server_url = "http://139.100.234.22"

# Try to send a command via the API to update files
# First, let's check what endpoints are available
endpoints = [
    "/api/deploy",
    "/api/update",
    "/api/pull",
    "/deploy",
    "/update",
]

for endpoint in endpoints:
    url = f"{server_url}{endpoint}"
    try:
        r = requests.post(url, json={"repo": "https://github.com/buchatskiii/buchatskiii.github.io.git"}, timeout=5)
        print(f"POST {url}: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"POST {url}: Error - {e}")

# Also try GET
for endpoint in endpoints:
    url = f"{server_url}{endpoint}"
    try:
        r = requests.get(url, timeout=5)
        print(f"GET {url}: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"GET {url}: Error - {e}")

print("\nDone. Files are already on GitHub (master branch).")
print("To update the server, you need SSH access or use the hosting panel.")
print("\nGitHub repo: https://github.com/buchatskiii/buchatskiii.github.io.git")
print("Files to copy to /var/www/english-tutor/html/:")
print("  - index.html")
print("  - styles.css")
