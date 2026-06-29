#!/usr/bin/env python3
"""Create a real ICO file from the PNG favicon."""
import struct
import zlib
import os

# Read the existing PNG file
png_path = r"C:\Users\dlyav\Desktop\english-tutor\favicon.ico"
with open(png_path, "rb") as f:
    png_data = f.read()

# PNG is 32x32, we'll create a proper ICO with the PNG embedded
# ICO header: reserved(2) + type(2) + count(2)
# ICO directory entry: width(1) + height(1) + colors(1) + reserved(1) + planes(2) + bpp(2) + size(4) + offset(4)

width = 32
height = 32
bpp = 32

# ICO header
ico_header = struct.pack('<HHH', 0, 1, 1)  # reserved=0, type=1(ICO), count=1

# Directory entry
data_size = len(png_data)
data_offset = 6 + 16  # header + 1 entry
entry = struct.pack('<BBBBHHII', 
    width if width < 256 else 0,
    height if height < 256 else 0,
    0,  # colors
    0,  # reserved
    1,  # planes
    bpp,
    data_size,
    data_offset
)

# Combine
ico_data = ico_header + entry + png_data

# Write the real ICO file
ico_path = r"C:\Users\dlyav\Desktop\english-tutor\favicon.ico"
with open(ico_path, "wb") as f:
    f.write(ico_data)

print(f"Created real ICO file: {len(ico_data)} bytes")
print(f"First bytes: {ico_data[:8].hex()}")

# Verify
with open(ico_path, "rb") as f:
    header = f.read(4)
    print(f"Header: {header.hex()}")
    assert header == b'\x00\x00\x01\x00', "Not a valid ICO file!"
    print("✓ Valid ICO file created!")
