from PIL import Image, ImageDraw
import os

def create_vertical_split_masks(n, width=1024, height=1024, out_dir="."):
    mask_files = []
    chunk_width = width // n
    for i in range(n):
        img = Image.new("L", (width, height), 0) # Black
        draw = ImageDraw.Draw(img)
        x0 = i * chunk_width
        x1 = (i + 1) * chunk_width if i < n - 1 else width
        draw.rectangle([x0, 0, x1, height], fill=255) # White
        filename = f"apollo_mask_{i}.png"
        filepath = os.path.join(out_dir, filename)
        img.save(filepath)
        mask_files.append(filepath)
    return mask_files

print(create_vertical_split_masks(3))
