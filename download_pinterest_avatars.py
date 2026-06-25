import requests
import re
import os
import paramiko

# Pinterest URLs
pins = [
    "https://ru.pinterest.com/pin/3166662233629071/",
    "https://ru.pinterest.com/pin/334814553569399291/",
    "https://ru.pinterest.com/pin/27795722696276906/",
    "https://ru.pinterest.com/pin/6966574421586254/",
    "https://ru.pinterest.com/pin/19492210988768302/",
    "https://ru.pinterest.com/pin/5207355816000886/"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

os.makedirs("avatars", exist_ok=True)

for i, url in enumerate(pins):
    try:
        print(f"\n[{i+1}] Загружаю {url}...")
        resp = requests.get(url, headers=headers, timeout=15)
        
        # Ищем изображение в HTML
        # Pinterest хранит изображение в meta og:image или в JSON данных
        patterns = [
            r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"',
            r'"image_url":"([^"]+)"',
            r'"images":\{"orig":\{"url":"([^"]+)"',
            r'"url":"([^"]+\.(jpg|jpeg|png|webp))"',
            r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*hCL[^"]*"',
        ]
        
        img_url = None
        for pattern in patterns:
            matches = re.findall(pattern, resp.text)
            if matches:
                img_url = matches[0]
                if isinstance(img_url, tuple):
                    img_url = img_url[0]
                print(f"  Найдено изображение: {img_url[:100]}...")
                break
        
        if img_url:
            # Скачиваем
            img_resp = requests.get(img_url, headers=headers, timeout=15)
            ext = img_url.split('.')[-1].split('?')[0][:4]
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                ext = 'jpg'
            
            filename = f"avatars/student_{i+1}.{ext}"
            with open(filename, 'wb') as f:
                f.write(img_resp.content)
            print(f"  ✅ Сохранено: {filename} ({len(img_resp.content)} bytes)")
        else:
            print(f"  ❌ Не удалось найти изображение в HTML")
            # Сохраняем HTML для отладки
            with open(f"avatars/debug_{i+1}.html", 'w', encoding='utf-8') as f:
                f.write(resp.text)
            print(f"  HTML сохранён для отладки")
            
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")

print("\n✅ Готово!")
