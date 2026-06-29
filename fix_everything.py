#!/usr/bin/env python3
"""Complete fix: proper HTML structure, proper CSS, proper JS."""
import paramiko

password = "qmc67Ra9TYas"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
sftp = client.open_sftp()

# Read current files
with sftp.open("/var/www/englishpro/index.html", "r") as f:
    html = f.read().decode("utf-8")

with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# ===== 1. Fix HTML: proper about-content structure =====
# Find the exact section and replace it completely
import re

# Find the about section - from <section class="about" to next <section
about_section_match = re.search(r'<section class="about section".*?</section>', html, re.DOTALL)
if about_section_match:
    old_about = about_section_match.group(0)
    
    # Create new about section with proper structure
    new_about = '''    <section class="about section" id="about">
        <div class="container">
            <div class="section-header">
                <span class="section-tag">Обо мне</span>
                <h2>Ваш проводник в мир <br>английского языка</h2>
            </div>
            <div class="about-content">
                <div class="about-video-wrapper">
                    <video id="aboutVideo" class="about-video" autoplay playsinline preload="auto" controls poster="/images/teacher.jpg">
                        <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                    </video>
                </div>
                <div class="about-text">
                    <h3>Привет! Меня зовут Анна Смирнова</h3>
                    <p>Я дипломированный преподаватель английского языка с многолетним опытом работы. Моя специализация — подготовка к ОГЭ и ЕГЭ, а также международным экзаменам (IELTS, TOEFL, Cambridge).</p>
                    <p>За годы работы я помогла сотням учеников поступить в ведущие вузы России и мира. Моя методика основана на глубоком понимании структуры экзаменов и индивидуальном подходе к каждому ученику.</p>
                    
                    <div class="about-achievements">
                        <div class="achievement-item">
                            <span class="achievement-icon">🎓</span>
                            <div>
                                <strong>МГУ им. М.В. Ломоносова</strong>
                                <p>Факультет иностранных языков, красный диплом</p>
                            </div>
                        </div>
                        <div class="achievement-item">
                            <span class="achievement-icon">🌍</span>
                            <div>
                                <strong>Стажировка в Великобритании</strong>
                                <p>University of Cambridge, 6 месяцев</p>
                            </div>
                        </div>
                        <div class="achievement-item">
                            <span class="achievement-icon">📝</span>
                            <div>
                                <strong>Эксперт ЕГЭ</strong>
                                <p>Член экспертной комиссии по проверке ЕГЭ (2018-2023)</p>
                            </div>
                        </div>
                        <div class="achievement-item">
                            <span class="achievement-icon">🏅</span>
                            <div>
                                <strong>Автор методических пособий</strong>
                                <p>3 опубликованных пособия по подготовке к ЕГЭ</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>'''
    
    html = html.replace(old_about, new_about)
    print("✅ HTML about section completely replaced with proper structure")
else:
    print("⚠️ Could not find about section")

# ===== 2. Fix CSS: add proper about-content styles =====
# Remove ALL existing about-content and about-video CSS
css = re.sub(r'\.about-content\s*\{[^}]*\}', '', css)
css = re.sub(r'\.about-content\s*\.about-image[^}]*\}', '', css)
css = re.sub(r'\.about-content\s*\.about-image\s+img[^}]*\}', '', css)
css = re.sub(r'\.about-content\s*\.about-text[^}]*\}', '', css)
css = re.sub(r'\.about-video-wrapper[^}]*\}', '', css)
css = re.sub(r'\.about-video[^}]*\}', '', css)
css = re.sub(r'\.video-hint[^}]*\}', '', css)
css = re.sub(r'\.about-video-wrapper:hover[^}]*\}', '', css)
css = re.sub(r'\.about-video::-webkit-media-controls[^}]*\}', '', css)
css = re.sub(r'\.about-video::-webkit-media-controls-panel[^}]*\}', '', css)
css = re.sub(r'@media[^}]*\{[^}]*\.about-video-wrapper[^}]*\}', '', css)
css = re.sub(r'@media[^}]*\{[^}]*\.about-content[^}]*\}', '', css)
css = re.sub(r'@media[^}]*\{[^}]*\.about-images[^}]*\}', '', css)
css = re.sub(r'\.about-images[^}]*\}', '', css)

# Add new CSS at the end of the file (before any @media)
new_css = '''
/* ===== VIDEO IN ABOUT SECTION ===== */
.about-content {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    gap: 60px;
}

.about-video-wrapper {
    flex: 0 0 auto;
    width: 320px;
    max-width: 40%;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    background: #000;
    position: sticky;
    top: 100px;
}

.about-video {
    width: 100%;
    height: auto;
    display: block;
    aspect-ratio: 9/16;
    object-fit: cover;
    background: #1a1a2e;
    cursor: pointer;
}

.about-text {
    flex: 1;
    min-width: 0;
}

.about-video::-webkit-media-controls {
    background: rgba(0,0,0,0.3);
}

.about-video::-webkit-media-controls-panel {
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
}

@media (max-width: 768px) {
    .about-content {
        flex-direction: column;
        gap: 30px;
    }
    .about-video-wrapper {
        width: 100%;
        max-width: 300px;
        margin: 0 auto;
        position: static;
    }
}
'''

css += new_css
print("✅ CSS updated")

# ===== 3. Write JS =====
new_js = '''// ===== VIDEO: autoplay with sound at 33% =====
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;

    // Set volume to 33%
    video.volume = 0.33;
    video.muted = false;

    // IntersectionObserver: autoplay when visible
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                video.play().catch(function() {});
            } else {
                video.pause();
            }
        });
    }, { threshold: 0.3 });

    observer.observe(video);

    // Try to play immediately if already visible
    setTimeout(function() {
        video.play().catch(function() {});
    }, 500);
})();
'''

with sftp.open("/var/www/englishpro/video_fix.js", "w") as f:
    f.write(new_js.encode("utf-8"))
print("✅ video_fix.js written")

# Write files
with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ index.html saved")

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))
print("✅ styles.css saved")

sftp.close()
client.close()

# Reload nginx
client2 = paramiko.SSHClient()
client2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client2.connect('139.100.234.22', 22, 'root', password, look_for_keys=False, allow_agent=False)
stdin, stdout, stderr = client2.exec_command('nginx -t && systemctl reload nginx')
print("✅ Nginx reloaded")
client2.close()

print("\n✅ All fixed! Video on LEFT, text on RIGHT, sound at 33%")
