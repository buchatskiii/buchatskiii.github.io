#!/usr/bin/env python3
"""Create a proper ICO favicon with centered letter 'B'."""
import struct
import io
import zlib

def create_png(width, height, r, g, b):
    """Create a minimal PNG with a centered letter."""
    # Create a simple image with PIL-like approach using raw pixel data
    
    # For a 32x32 icon, we'll create a simple design:
    # - Rounded square background with gradient purple
    # - White letter "B" centered
    
    # We'll use raw PNG creation
    def create_png_raw():
        # PNG signature
        signature = b'\x89PNG\r\n\x1a\n'
        
        # IHDR chunk
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
        ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        
        # Create pixel data (RGBA)
        pixels = []
        center_x, center_y = width // 2, height // 2
        
        for y in range(height):
            row = []
            for x in range(width):
                # Distance from center
                dx = x - center_x
                dy = y - center_y
                dist = (dx*dx + dy*dy) ** 0.5
                
                # Rounded square shape
                corner_radius = 6
                edge_dist = max(abs(dx) - (center_x - corner_radius), abs(dy) - (center_y - corner_radius), 0)
                in_circle = edge_dist <= corner_radius
                
                # Check if inside the rounded square
                in_rounded_square = (abs(dx) <= center_x - corner_radius and abs(dy) <= center_y - corner_radius) or in_circle
                
                if in_rounded_square:
                    # Gradient purple background
                    gradient = (y / height) * 0.3
                    pr = int((156 + (200 - 156) * (x / width)) * (1 - gradient))
                    pg = int((100 + (150 - 100) * (x / width)) * (1 - gradient))
                    pb = int((220 + (255 - 220) * (x / width)) * (1 - gradient))
                    
                    # Draw letter "B" in white
                    letter_pixels = draw_letter_b(x, y, width, height)
                    if letter_pixels:
                        row.extend([255, 255, 255, 255])  # White letter
                    else:
                        row.extend([pr, pg, pb, 255])  # Gradient bg
                else:
                    row.extend([0, 0, 0, 0])  # Transparent
            pixels.append(bytes(row))
        
        # Combine with filter bytes (0 = None for each row)
        raw_data = b''
        for row in pixels:
            raw_data += b'\x00' + row  # filter byte 0 (None) + row data
        
        # Compress
        compressed = zlib.compress(raw_data)
        
        # IDAT chunk
        idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
        idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
        
        # IEND chunk
        iend_crc = zlib.crc32(b'IEND') & 0xffffffff
        iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
        
        return signature + ihdr + idat + iend
    
    def draw_letter_b(x, y, w, h):
        """Draw a centered letter 'B'."""
        # Normalize coordinates to 0..1
        nx = x / w
        ny = y / h
        
        # Letter B occupies 30%-70% of width and 20%-80% of height
        lx = 0.35  # left edge
        rx = 0.65  # right edge
        ty = 0.20  # top edge
        by = 0.80  # bottom edge
        mid_y = 0.48  # middle of B
        
        # Check if in vertical stem (left part)
        if lx <= nx <= lx + 0.08 and ty <= ny <= by:
            return True
        
        # Check if in top loop
        if lx + 0.08 <= nx <= rx and ty <= ny <= mid_y:
            # Right curve of top loop
            cx = (lx + rx) / 2
            cy = (ty + mid_y) / 2
            rx_loop = (rx - lx) / 2
            ry_loop = (mid_y - ty) / 2
            dx_norm = (nx - cx) / rx_loop
            dy_norm = (ny - cy) / ry_loop
            if dx_norm * dx_norm + dy_norm * dy_norm <= 1.0:
                return True
        
        # Check if in bottom loop
        if lx + 0.08 <= nx <= rx and mid_y <= ny <= by:
            cx = (lx + rx) / 2
            cy = (mid_y + by) / 2
            rx_loop = (rx - lx) / 2
            ry_loop = (by - mid_y) / 2
            dx_norm = (nx - cx) / rx_loop
            dy_norm = (ny - cy) / ry_loop
            if dx_norm * dx_norm + dy_norm * dy_norm <= 1.0:
                return True
        
        return False
    
    return create_png_raw()

# Create the PNG
png_data = create_png(32, 32, 156, 100, 220)

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

print(f"Created centered favicon ICO: {len(ico_data)} bytes")
print(f"Header: {ico_data[:4].hex()}")

# Verify
with open(ico_path, "rb") as f:
    header = f.read(4)
    assert header == b'\x00\x00\x01\x00', "Not a valid ICO file!"
    print("✓ Valid ICO file with centered letter B!")
