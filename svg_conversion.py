import os
import cairosvg
from PIL import Image, ImageDraw

PATH = "eu"
RADIUS = 30  # Corner rounding radius in pixels
CROP_WIDTH, CROP_HEIGHT = 300, 200  # Desired output size

def round_corners(im: Image.Image, radius: int) -> Image.Image:
    """
    Apply rounded corners to an RGBA image and return the new image.
    """
    im = im.convert("RGBA")
    w, h = im.size

    # Create a same-size transparent mask
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)

    # Apply mask as alpha channel
    im.putalpha(mask)
    return im

svg_files = [f for f in os.listdir(f"{PATH}/submaps") if f.lower().endswith(".svg")]

for file in svg_files:

    png_path = f"{PATH}/submaps/{file[:-4]}.png"
    svg_path = f"{PATH}/submaps/{file}"

    # Convert SVG → PNG
    cairosvg.svg2png(
        url=svg_path,
        write_to=png_path,
        output_height=200
    )

    # Open image and crop from center
    img = Image.open(png_path)
    w, h = img.size
    left   = (w - CROP_WIDTH)  // 2
    upper  = (h - CROP_HEIGHT) // 2
    right  = left + CROP_WIDTH
    lower  = upper + CROP_HEIGHT

    cropped = img.crop((left, upper, right, lower))

    # Apply rounded corners
    rounded = round_corners(cropped, radius=RADIUS)

    # Save (preserves transparency)
    rounded.save(png_path, format="PNG")