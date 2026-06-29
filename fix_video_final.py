#!/usr/bin/env python3
"""Fix video: make vertical, add controls, autoplay on scroll."""
import paramiko
import re

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

# ===== 1. UPDATE HTML: add autoplay, controls, remove overlay =====
# Find the video wrapper section
old_video_html = '''                    <div class="about-video-wrapper">
                        <video id="aboutVideo" class="about-video" muted playsinline preload="metadata" poster="/images/teacher.jpg">
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                        </video>
                        <div class="video-play-overlay" id="videoPlayOverlay">
                            <span class="play-icon">▶</span>
                            <span class="play-text">Нажмите, чтобы посмотреть</span>
                        </div>
                    </div>'''

new_video_html = '''                    <div class="about-video-wrapper">
                        <video id="aboutVideo" class="about-video" autoplay muted playsinline preload="auto" controls poster="/images/teacher.jpg">
                            <source src="/videos/povelitel_vselennoy.mp4" type="video/mp4">
                        </video>
                        <div class="video-hint">Нажмите на видео, чтобы включить звук</div>
                    </div>'''

if old_video_html in html:
    html = html.replace(old_video_html, new_video_html)
    print("✅ HTML video section updated")
else:
    print("⚠️ Could not find exact old video HTML, trying regex...")
    # Fallback: replace using regex
    pattern = r'<div class="about-video-wrapper">.*?</div>\s*</div>'
    replacement = new_video_html + '\n                    </div>'
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    print("✅ HTML video section updated via regex")

# ===== 2. UPDATE CSS: make video vertical with proper styling =====
# Remove old video CSS section and add new one
old_css_start = '/* ===== VIDEO IN ABOUT SECTION =====' 
old_css_end = '/* ===== ABOUT SECTION ====='

# Find and replace the video CSS section
video_css_pattern = r'/\* ===== VIDEO IN ABOUT SECTION =====.*?(?=/\* =====|$)'
new_video_css = '''/* ===== VIDEO IN ABOUT SECTION ===== */
.about-images {
    display: flex;
    flex-direction: column;
    gap: 20px;
    flex: 1;
    min-width: 300px;
    max-width: 400px;
}

.about-video-wrapper {
    position: relative;
    width: 100%;
    max-width: 360px;
    margin: 0 auto;
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-lg);
    background: #000;
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

.video-hint {
    position: absolute;
    bottom: 60px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
    white-space: nowrap;
}

.about-video-wrapper:hover .video-hint {
    opacity: 1;
}

/* Video controls styling */
.about-video::-webkit-media-controls {
    background: rgba(0,0,0,0.3);
}

.about-video::-webkit-media-controls-panel {
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
}

@media (max-width: 768px) {
    .about-images {
        max-width: 100%;
        min-width: unset;
    }
    .about-video-wrapper {
        max-width: 300px;
    }
}
'''

css = re.sub(video_css_pattern, new_video_css, css, flags=re.DOTALL)
print("✅ CSS video section updated")

# ===== 3. REPLACE video_fix.js with new IntersectionObserver version =====
new_video_js = '''// ===== VIDEO: autoplay on scroll with IntersectionObserver =====
(function() {
    var video = document.getElementById('aboutVideo');
    if (!video) return;

    video.volume = 0.5;
    var hasInteracted = false;
    var wasPlaying = false;

    // Listen for first user interaction to enable sound
    document.addEventListener('click', function() {
        hasInteracted = true;
        if (video.paused && wasPlaying) {
            video.muted = false;
            video.play().catch(function() {});
        }
    }, { once: true });

    document.addEventListener('touchstart', function() {
        hasInteracted = true;
        if (video.paused && wasPlaying) {
            video.muted = false;
            video.play().catch(function() {});
        }
    }, { once: true });

    // Click on video to toggle sound
    video.addEventListener('click', function() {
        if (video.muted) {
            video.muted = false;
            video.play().catch(function() {});
        } else {
            video.muted = true;
        }
    });

    // IntersectionObserver: autoplay when visible
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                // Video is visible - play it
                video.play().catch(function() {});
                wasPlaying = true;
            } else {
                // Video is not visible - pause it
                video.pause();
                wasPlaying = false;
            }
        });
    }, { threshold: 0.3 });

    observer.observe(video);

    // Also try to play immediately if already visible
    setTimeout(function() {
        video.play().catch(function() {});
    }, 1000);
})();
'''

try:
    with sftp.open("/var/www/englishpro/video_fix.js", "w") as f:
        f.write(new_video_js.encode("utf-8"))
    print("✅ video_fix.js updated")
except Exception as e:
    print(f"⚠️ Could not write video_fix.js: {e}")

# Write updated files
with sftp.open("/var/www/englishpro/index.html", "w") as f:
    f.write(html.encode("utf-8"))
print("✅ index.html saved")

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))
print("✅ styles.css saved")

sftp.close()
client.close()
print("\n✅ All files updated! Reloading nginx...")
