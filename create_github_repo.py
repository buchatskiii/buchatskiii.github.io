#!/usr/bin/env python3
"""Создаём репозиторий на GitHub и пушим код"""
import subprocess, os, json, urllib.request

TOKEN = "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"
REPO_NAME = "english-tutor"

# Создаём репозиторий через API
data = json.dumps({
    "name": REPO_NAME,
    "description": "Сайт-визитка репетитора по английскому языку. Подготовка к ОГЭ/ЕГЭ.",
    "private": False,
    "has_issues": True,
    "has_projects": False,
    "has_wiki": False
}).encode()

req = urllib.request.Request(
    "https://api.github.com/user/repos",
    data=data,
    headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
)

try:
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    print(f"✅ Репозиторий создан: {result['html_url']}")
    clone_url = result['clone_url']
except urllib.error.HTTPError as e:
    if e.code == 422:
        print("⚠️ Репозиторий уже существует, пробуем подключиться...")
        clone_url = f"https://github.com/{json.loads(urllib.request.urlopen(urllib.request.Request('https://api.github.com/user', headers={'Authorization': f'token {TOKEN}'})).read())['login']}/{REPO_NAME}.git"
    else:
        print(f"❌ Ошибка: {e.code} - {e.read().decode()}")
        exit(1)

# Меняем директорию
os.chdir(r"C:\Users\dlyav\Desktop\english-tutor")

# Удаляем старый origin если есть
subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)

# Добавляем origin
subprocess.run(["git", "remote", "add", "origin", clone_url])

# Коммитим
subprocess.run(["git", "add", "-A"])
result = subprocess.run(["git", "commit", "-m", "Initial commit: сайт-визитка репетитора по английскому языку"], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)

# Пушим
print("\n🚀 Пушим на GitHub...")
result = subprocess.run(["git", "push", "-u", "origin", "master"], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
else:
    print("✅ Успешно запушено!")
