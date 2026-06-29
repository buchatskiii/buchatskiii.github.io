#!/usr/bin/env python3
"""Test form submission via API."""
import requests
import json

# Test the API directly
url = "https://beklox.ru/api/lead"
data = {
    "name": "Тест",
    "phone": "+7 (999) 123-45-67",
    "email": "test@example.com",
    "goal": "ege",
    "message": "Тестовое сообщение",
    "privacy": True
}

headers = {
    "Content-Type": "application/json",
    "Origin": "https://beklox.ru",
    "Referer": "https://beklox.ru/"
}

print(f"POST {url}")
print(f"Data: {json.dumps(data, ensure_ascii=False, indent=2)}")

try:
    response = requests.post(url, json=data, headers=headers, timeout=10)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Also test health endpoint
try:
    r = requests.get("https://beklox.ru/health", timeout=10)
    print(f"\nHealth check: {r.status_code} - {r.text}")
except Exception as e:
    print(f"Health error: {e}")
