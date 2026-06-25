import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

# Читаем HTML
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

# Ищем секцию about
if 'about-image' in html:
    # Найдём блок about-image
    import re
    match = re.search(r'<div class="about-image">(.*?)</div>\s*</div>\s*</div>\s*<div class="about-text"', html, re.DOTALL)
    if match:
        print("=== Текущий about-image блок ===")
        print(match.group(0)[:500])
    else:
        print("about-image найден, но не смог распарсить")
else:
    print("about-image НЕ НАЙДЕН в HTML!")
    # Поищем что-то похожее
    if 'about' in html.lower():
        print("Слово 'about' найдено")
    if 'video' in html:
        print("Слово 'video' найдено")

# Проверим, есть ли видео-секция
if 'video-section' in html:
    print("\n⚠️ Старая видео-секция всё ещё есть!")
    
# Проверим, есть ли наш новый код
if 'aboutVideoWrapper' in html:
    print("\n✅ aboutVideoWrapper найден — видео уже вставлено!")
else:
    print("\n❌ aboutVideoWrapper НЕ НАЙДЕН — нужно вставить видео заново")
    
    # Найдём точный блок для замены
    about_match = re.search(r'<div class="about-image">.*?<img[^>]*>.*?<div class="experience-badge">', html, re.DOTALL)
    if about_match:
        print("\nНайден блок с фото. Заменяю...")
        
        old_block = about_match.group(0)
        new_block = """<div class="about-image">
                    <div class="about-video-wrapper" id="aboutVideoWrapper">
                        <video class="about-video" id="aboutVideo" muted playsinline preload="auto" poster="/images/video-poster.jpg">
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                            Ваш браузер не поддерживает видео.
                        </video>
                        <div class="video-play-btn" id="videoPlayBtn">
                            <span class="play-icon">▶</span>
                            <span class="play-text">Нажмите, чтобы посмотреть обращение</span>
                        </div>
                    </div>
                    <div class="experience-badge">"""
        
        html = html.replace(old_block, new_block)
        
        # Удаляем старую видео-секцию
        html = re.sub(r'<!-- Video Section -->.*?<section class="contact section"', '<section class="contact section"', html, flags=re.DOTALL)
        
        with sftp.open("/var/www/englishpro/index.html", "w") as f:
            f.write(html.encode("utf-8"))
        print("✅ HTML обновлён!")
    else:
        print("Не удалось найти блок с фото для замены")
        # Выведем весь about-image блок
        all_about = re.search(r'<div class="about-image">(.*?)</div>\s*</div>', html, re.DOTALL)
        if all_about:
            print("Содержимое about-image:")
            print(all_about.group(0))

sftp.close()
ssh.close()
