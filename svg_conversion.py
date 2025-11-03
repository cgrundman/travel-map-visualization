import os
import cairosvg
from PIL import Image

PATH = "de"

svg_files = [f for f in os.listdir(f"{PATH}/submaps") if f.lower().endswith(".svg")]
for file in svg_files:

    cairosvg.svg2png(
        url=f"{PATH}/submaps/{file}", 
        write_to=f"{PATH}/submaps/{file[:-4]}.png", 
        output_height=200
    )

    img = Image.open(f"{PATH}/submaps/{file[:-4]}.png",)

    crop_width, crop_height = 300, 200  # desired output size

    w, h = img.size
    left   = (w - crop_width)  // 2
    upper  = (h - crop_height) // 2
    right  = left + crop_width
    lower  = upper + crop_height

    cropped = img.crop((left, upper, right, lower))
    cropped.save(f"{PATH}/submaps/{file[:-4]}.png",)