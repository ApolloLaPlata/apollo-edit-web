import math
import io
import base64
from PIL import Image, ImageDraw, ImageFont

# Create dummy images
pil_imgs = [
    Image.new("RGB", (300, 600), (255, 0, 0)),
    Image.new("RGB", (800, 300), (0, 255, 0)),
    Image.new("RGB", (400, 400), (0, 0, 255))
]

num_imgs = len(pil_imgs)
cols = math.ceil(math.sqrt(num_imgs))
rows = math.ceil(num_imgs / cols)

w, h = 512, 512
grid = Image.new("RGB", size=(cols * w, rows * h), color=(255, 255, 255))
for i, img in enumerate(pil_imgs):
    img.thumbnail((w, h), Image.Resampling.LANCZOS)
    img_smart = Image.new("RGB", (w, h), (255, 255, 255))
    offset_x = (w - img.width) // 2
    offset_y = (h - img.height) // 2
    img_smart.paste(img, (offset_x, offset_y))
    
    # Quadrant Labelling
    draw = ImageDraw.Draw(img_smart)
    label = f"Image {i+1}"
    
    # Use default font but make it visible (draw multiple times for bold or just use default)
    # Background rect
    draw.rectangle([(10, 10), (90, 35)], fill=(0,0,0))
    draw.text((15, 15), label, fill=(255,255,255))
    
    grid.paste(img_smart, box=(i % cols * w, i // cols * h))

grid.save("test_grid_output.jpg")
print("Saved test_grid_output.jpg")
