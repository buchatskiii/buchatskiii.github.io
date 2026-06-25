import urllib.request, urllib.parse
import re

raw_url = 'https://videovssylku.ru/v/повелитель-вселенной.xhc8'
parsed = urllib.parse.urlparse(raw_url)
path = urllib.parse.quote(parsed.path, safe='/:')
url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=10)
html = resp.read().decode('utf-8', errors='ignore')

# Ищем все mp4/webm ссылки
for m in re.finditer(r'(https?://[^"\'<>]+\.(mp4|webm|ogg)[^"\'<>]*)', html):
    print('Видео:', m.group(1))

# Ищем data-src или data-video
for m in re.finditer(r'data-(?:src|video|file)="([^"]+)"', html):
    print('data-*:', m.group(1))

# Ищем прямые ссылки на видеофайлы
for m in re.finditer(r'(https?://[^"\'<>]+/v/[^"\'<>]+)', html):
    link = m.group(1)
    if any(x in link for x in ['.mp4', '.webm', 'video', 'media', 'download']):
        print('media link:', link)

# Ищем oembed
for m in re.finditer(r'oembed.*?url=([^"\'&]+)', html):
    print('oembed:', urllib.parse.unquote(m.group(1)))

# Ищем кнопку скачать/прямую ссылку
for m in re.finditer(r'href="([^"]+)"[^>]*>Скачать|href="([^"]+)"[^>]*>Download|href="([^"]+)"[^>]*>Прямая', html):
    print('download:', m.groups())

# Покажем кусок с video тегом
idx = html.find('<video')
if idx > 0:
    print('\n--- video tag ---')
    print(html[idx:idx+600])

# Ищем source внутри video
for m in re.finditer(r'<source[^>]+src="([^"]+)"', html):
    print('source src:', m.group(1))
