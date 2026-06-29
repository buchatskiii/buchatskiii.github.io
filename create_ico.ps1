Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap(32, 32)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'HighQuality'
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 37, 99, 235))
$g.FillEllipse($brush, 0, 0, 31, 31)
$font = New-Object System.Drawing.Font('Arial', 22, [System.Drawing.FontStyle]::Bold)
$white = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$g.DrawString('B', $font, $white, 4, 2)
$g.Dispose()
$bmp.Save('C:\Users\dlyav\Desktop\english-tutor\favicon.ico', [System.Drawing.Imaging.ImageFormat]::Icon)
$bmp.Dispose()
Write-Host 'ICO created successfully'
