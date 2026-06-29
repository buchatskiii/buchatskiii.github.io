#!/usr/bin/env python3
"""Upload files to server via HTTP API."""
import requests
import os

local_dir = r"C:\Users\dlyav\Desktop\english-tutor"
server_url = "http://139.100.234.22"

files_to_upload = ["index.html", "styles.css"]

for filename in files_to_upload:
    local_path = os.path.join(local_dir, filename)
    
    # Try to upload via PUT request to /uploads/ path
    with open(local_path, "rb") as f:
        content = f.read()
    
    # Try different endpoints
    endpoints = [
        f"{server_url}/uploads/{filename}",
        f"{server_url}/api/upload/{filename}",
        f"{server_url}/upload/{filename}",
    ]
    
    for url in endpoints:
        try:
            r = requests.put(url, data=content, timeout=5)
            print(f"PUT {url}: {r.status_code}")
        except Exception as e:
            print(f"PUT {url}: Error - {e}")
    
    # Try POST with multipart
    try:
        r = requests.post(
            f"{server_url}/api/upload",
            files={"file": (filename, open(local_path, "rb"))},
            timeout=5
        )
        print(f"POST /api/upload: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"POST /api/upload: Error - {e}")

print("\nDone trying to upload files.")
print("\nAlternative: You can use the server's panel to upload files.")
print("Or install WinSCP and connect with your server credentials.")
