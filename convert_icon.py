import sys
from PIL import Image

def convert_to_ico(png_path, ico_path):
    try:
        img = Image.open(png_path)
        # Ensure image is square and resize if necessary to standard icon sizes
        icon_sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
        img.save(ico_path, format="ICO", sizes=icon_sizes)
        print(f"Successfully converted to {ico_path}")
    except Exception as e:
        print(f"Error converting to ICO: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_icon.py <input.png> <output.ico>")
    else:
        convert_to_ico(sys.argv[1], sys.argv[2])
