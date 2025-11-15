"""
Create a favicon from FontAwesome brain icon
"""

from PIL import Image, ImageDraw
import base64
from io import BytesIO

# Create a 32x32 image with transparency
size = 32
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a simplified brain icon using shapes
# Blue/cyan gradient color for AI theme
color = (88, 166, 255, 255)  # RGB + Alpha

# Left hemisphere (simplified rounded rectangle)
left_points = [
    (6, 10), (6, 22),  # left side
    (8, 26), (10, 28), (12, 28),  # bottom curve
    (14, 28), (14, 10),  # right side
    (12, 8), (10, 6), (8, 6), (6, 8)  # top curve
]
draw.polygon(left_points, fill=color)

# Right hemisphere
right_points = [
    (18, 10), (18, 28),  # left side
    (20, 28), (22, 28), (24, 26), (26, 22),  # bottom curve
    (26, 10), (24, 6), (22, 6), (20, 8), (18, 10)  # top curve
]
draw.polygon(right_points, fill=color)

# Center connection
draw.rectangle([14, 14, 18, 22], fill=color)

# Add highlight dots for detail
highlight = (150, 200, 255, 255)
draw.ellipse([8, 12, 10, 14], fill=highlight)
draw.ellipse([22, 12, 24, 14], fill=highlight)

# Save as ICO
output_path = 'AI_infrastructure/static/favicon.ico'
img.save(output_path, format='ICO', sizes=[(32, 32)])

print(f"✅ Created favicon at: {output_path}")
print(f"   Icon: Brain (AI/Intelligence theme)")
print(f"   Size: 32x32 pixels")
print(f"   Color: Blue (#58A6FF - accent-primary)")
