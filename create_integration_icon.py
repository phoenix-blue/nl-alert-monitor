#!/usr/bin/env python3
"""
Creates icon for NL-Alert integration for Home Assistant Brands repository.
This creates both the standard (256x256) and hDPI (512x512) versions.
"""

from PIL import Image, ImageDraw, ImageFont
import math

def create_gradient_background(size, color1, color2):
    """Create a gradient background from color1 to color2."""
    gradient = Image.new('RGBA', size)
    draw = ImageDraw.Draw(gradient)
    
    for i in range(size[1]):
        ratio = i / size[1]
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        a = int(color1[3] * (1 - ratio) + color2[3] * ratio)
        draw.rectangle([(0, i), (size[0], i+1)], fill=(r, g, b, a))
    
    return gradient

def create_wind_pattern(size, color):
    """Create wind/smoke pattern lines."""
    pattern = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(pattern)
    
    # Create wavy lines to represent wind/smoke
    width = size[0]
    height = size[1]
    
    for y in range(int(height * 0.3), int(height * 0.7), int(height * 0.08)):
        points = []
        for x in range(0, width + 10, 5):
            wave_y = y + math.sin(x * 0.05) * (height * 0.03)
            points.append((x, wave_y))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=color, width=int(height * 0.015))
    
    return pattern

def create_warning_triangle(size, center, triangle_size, color):
    """Create a warning triangle with exclamation mark."""
    triangle = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(triangle)
    
    # Triangle coordinates
    cx, cy = center
    half_size = triangle_size // 2
    height = int(triangle_size * 0.866)  # Height of equilateral triangle
    
    # Triangle points
    top = (cx, cy - height // 2)
    bottom_left = (cx - half_size, cy + height // 2)
    bottom_right = (cx + half_size, cy + height // 2)
    
    # Draw triangle with border
    draw.polygon([top, bottom_left, bottom_right], fill=color, outline=(255, 255, 255, 255), width=3)
    
    # Draw exclamation mark
    exc_width = int(triangle_size * 0.1)
    exc_height = int(triangle_size * 0.4)
    exc_x = cx - exc_width // 2
    exc_y = cy - exc_height // 2 - int(triangle_size * 0.1)
    
    # Exclamation line
    draw.rectangle([exc_x, exc_y, exc_x + exc_width, exc_y + exc_height], fill=(255, 255, 255, 255))
    
    # Exclamation dot
    dot_size = int(triangle_size * 0.08)
    dot_y = exc_y + exc_height + int(triangle_size * 0.08)
    draw.ellipse([cx - dot_size, dot_y, cx + dot_size, dot_y + dot_size * 2], fill=(255, 255, 255, 255))
    
    return triangle

def create_compass_rose(size, center, rose_size, color):
    """Create a simplified compass rose."""
    compass = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(compass)
    
    cx, cy = center
    radius = rose_size // 2
    
    # Main compass directions (N, E, S, W)
    directions = [
        (0, -radius),    # North
        (radius, 0),     # East
        (0, radius),     # South
        (-radius, 0)     # West
    ]
    
    for dx, dy in directions:
        x, y = cx + dx, cy + dy
        # Draw compass point
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=color)
        # Draw line to center
        draw.line([(cx, cy), (x, y)], fill=color, width=2)
    
    # Center circle
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color, outline=(255, 255, 255, 255), width=2)
    
    return compass

def create_nl_alert_icon(size):
    """Create the main NL-Alert icon."""
    # Dutch colors and emergency colors
    dutch_orange = (255, 102, 0, 255)      # Dutch orange
    dutch_blue = (0, 51, 153, 255)         # Dutch blue  
    dutch_white = (255, 255, 255, 255)     # White
    warning_red = (220, 53, 69, 255)       # Alert red
    smoke_gray = (108, 117, 125, 180)      # Semi-transparent smoke
    
    # Create base image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Create gradient background (Dutch flag inspired)
    bg_gradient = create_gradient_background((size, size), dutch_blue, dutch_orange)
    img = Image.alpha_composite(img, bg_gradient)
    
    # Add wind/smoke pattern
    wind_pattern = create_wind_pattern((size, size), smoke_gray)
    img = Image.alpha_composite(img, wind_pattern)
    
    # Add warning triangle (main element)
    triangle_size = int(size * 0.4)
    warning_triangle = create_warning_triangle((size, size), (size//2, size//2 - size//8), triangle_size, warning_red)
    img = Image.alpha_composite(img, warning_triangle)
    
    # Add compass rose (bottom right)
    compass_size = int(size * 0.2)
    compass_pos = (int(size * 0.75), int(size * 0.75))
    compass_rose = create_compass_rose((size, size), compass_pos, compass_size, dutch_white)
    img = Image.alpha_composite(img, compass_rose)
    
    # Add "NL" text (top left corner)
    draw = ImageDraw.Draw(img)
    try:
        # Try to use a good font
        font_size = int(size * 0.12)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text_x = int(size * 0.08)
    text_y = int(size * 0.08)
    
    # Draw text with outline for visibility
    outline_color = (0, 0, 0, 255)
    text_color = dutch_white
    
    # Draw outline
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                draw.text((text_x + dx, text_y + dy), "NL", font=font, fill=outline_color)
    
    # Draw main text
    draw.text((text_x, text_y), "NL", font=font, fill=text_color)
    
    return img

def create_icons():
    """Create both standard and hDPI icons."""
    
    # Create standard icon (256x256)
    print("Creating standard icon (256x256)...")
    icon_256 = create_nl_alert_icon(256)
    icon_256.save("images/icon.png", "PNG", optimize=True)
    print("✓ Created images/icon.png")
    
    # Create hDPI icon (512x512) 
    print("Creating hDPI icon (512x512)...")
    icon_512 = create_nl_alert_icon(512)
    icon_512.save("images/icon@2x.png", "PNG", optimize=True)
    print("✓ Created images/icon@2x.png")
    
    # Also create logo (same as icon for square logos per HA Brands guidelines)
    icon_256.save("images/logo.png", "PNG", optimize=True) 
    icon_512.save("images/logo@2x.png", "PNG", optimize=True)
    print("✓ Created logo files (same as icon)")
    
    print("\n🎨 Icon creation completed!")
    print("\nIcon specifications:")
    print("- Square aspect ratio (1:1)")
    print("- PNG format with transparency")
    print("- Dutch flag colors (orange/blue/white)")
    print("- Warning triangle for emergency alerts")
    print("- Wind pattern for smoke plume detection")
    print("- Compass rose for directional wind info")
    print("- 'NL' text for Dutch origin")
    
    print("\nNext steps for Home Assistant Brands:")
    print("1. Fork https://github.com/home-assistant/brands")
    print("2. Create custom_integrations/nl_alert/ folder")
    print("3. Upload icon.png, icon@2x.png, logo.png, logo@2x.png")
    print("4. Submit Pull Request")

if __name__ == "__main__":
    import os
    
    # Create images directory
    os.makedirs("images", exist_ok=True)
    
    create_icons()