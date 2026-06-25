import paramiko

host = "139.100.234.22"
port = 22
username = "root"
password = "qmc67Ra9TYas"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

sftp = ssh.open_sftp()

# Read current CSS
with sftp.open("/var/www/englishpro/styles.css", "r") as f:
    css = f.read().decode("utf-8")

# Add video section styles
video_css = """
/* Video Section */
.video-section {
    background: linear-gradient(135deg, #f8f9ff 0%, #eef1ff 100%);
    padding: 100px 0;
}

.video-wrapper {
    max-width: 800px;
    margin: 0 auto;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(99, 102, 241, 0.15);
    background: #000;
}

.video-player {
    width: 100%;
    display: block;
    max-height: 500px;
    object-fit: contain;
    background: #000;
}

.video-player::-webkit-media-controls-panel {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
}
"""

css += video_css

with sftp.open("/var/www/englishpro/styles.css", "w") as f:
    f.write(css.encode("utf-8"))

sftp.close()
ssh.close()
print("✅ CSS-стили для видео добавлены!")
print("🌐 http://139.100.234.22/")
