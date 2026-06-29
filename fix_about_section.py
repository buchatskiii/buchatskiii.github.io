#!/usr/bin/env python3
"""Fix about section: remove photo, keep only video with controls"""

with open("/var/www/englishpro/index.html") as f:
    content = f.read()

# 1. Remove the about-image div (photo + experience badge) - from <div class="about-image"> to </div> before about-video-wrapper
import re

# Remove the about-image block (photo + badge)
content = re.sub(
    r'<div class="about-image">\s*<img src="images/teacher\.jpg"[^>]*>\s*<div class="experience-badge">\s*<span class="exp-years">10\+</span>\s*<span class="exp-text">лет\s*<br>в профессии</span>\s*</div>\s*</div>',
    '',
    content
)

# 2. Remove muted from video tag, add controls
content = content.replace(
    '<video id="aboutVideo" class="about-video" muted playsinline preload="metadata" poster="/images/teacher.jpg" loop>',
    '<video id="aboutVideo" class="about-video" controls playsinline preload="metadata" poster="/images/teacher.jpg" loop>'
)

# 3. Remove the play overlay
content = re.sub(
    r'<div class="video-play-overlay"[^>]*>.*?</div>',
    '',
    content
)

with open("/var/www/englishpro/index.html", "w") as f:
    f.write(content)

print("SUCCESS: About section updated")
print("  - Removed photo and experience badge")
print("  - Added controls to video")
print("  - Removed play overlay")
