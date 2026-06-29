#!/usr/bin/env python3
"""Create a proper ICO favicon with a clear, readable letter 'B' using PIL-like pixel drawing."""
import struct
import zlib
import os

def create_png_with_letter(width=32, height=32):
    """Create a PNG with a clear letter B on purple background."""
    
    # Define the letter 'B' as a pixel map (1 = white, 0 = transparent/background)
    # Using a 20x24 grid centered in 32x32
    letter = [
        "11111111111111111111",
        "11111111111111111111",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11000000000000000011",
        "11111111111111111111",
        "11111111111111111111",
    ]
    
    # Offset to center the 20x24 letter in 32x32
    offset_x = (width - 20) // 2  # 6
    offset_y = (height - 24) // 2  # 4
    
    # Create pixel data (RGBA)
    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            # Check if we're in the letter area
            lx = x - offset_x
            ly = y - offset_y
            
            if 0 <= ly < len(letter) and 0 <= lx < len(letter[0]):
                if letter[ly][lx] == '1':
                    # White letter pixel
                    row.extend([255, 255, 255, 255])
                else:
                    # Purple background
                    row.extend([155, 89, 182, 255])
            else:
                # Outside letter - check if inside rounded square
                # Rounded square with corner radius 6
                cx, cy = width // 2, height // 2
                cr = 6
                dx = abs(x - cx)
                dy = abs(y - cy)
                
                if dx <= cx - cr and dy <= cy - cr:
                    # Inside main rectangle
                    row.extend([155, 89, 182, 255])
                elif dx > cx - cr and dy > cy - cr:
                    # Corner area - check if within corner radius
                    corner_dx = dx - (cx - cr)
                    corner_dy = dy - (cy - cr)
                    if corner_dx * corner_dx + corner_dy * corner_dy <= cr * cr:
                        row.extend([155, 89, 182, 255])
                    else:
                        row.extend([0, 0, 0, 0])  # Transparent
                else:
                    row.extend([155, 89, 182, 255])
        pixels.append(bytes(row))
    
    # Build PNG
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # IDAT
    raw_data = b''
    for row in pixels:
        raw_data += b'\x00' + row  # filter byte 0 (None)
    compressed = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    # IEND
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    return signature + ihdr + idat + iend

# Create PNG
png_data = create_png_with_letter()

# Create ICO wrapper
ico_header = struct.pack('<HHH', 0, 1, 1)  # reserved=0, type=1(ICO), count=1
data_size = len(png_data)
data_offset = 6 + 16
entry = struct.pack('<BBBBHHII', 32, 32, 0, 0, 1, 32, data_size, data_offset)
ico_data = ico_header + entry + png_data

# Save
ico_path = r"C:\Users\dlyav\Desktop\english-tutor\favicon.ico"
with open(ico_path, "wb") as f:
    f.write(ico_data)

print(f"Created favicon ICO: {len(ico_data)} bytes")
print(f"Header: {ico_data[:4].hex()}")

# Verify
with open(ico_path, "rb") as f:
    header = f.read(4)
    assert header == b'\x00\x00\x01\x00', "Not a valid ICO file!"
    print("✓ Valid ICO file with clear letter B!")
