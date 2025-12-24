import os
import cairosvg
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET
import re

PATH = "us"
RADIUS = 30  # Corner rounding radius in pixels
CROP_WIDTH, CROP_HEIGHT = 300, 200  # Desired output size
CROP_RATIO = CROP_WIDTH / CROP_HEIGHT
   
def crop_svg_center_no_viewbox(
    svg_in,
    png_out,
    target_ratio,
    raster_width=512,
    raster_height=320
):
    tree = ET.parse(svg_in)
    root = tree.getroot()

    # Handle namespace
    #if "}" in root.tag:
    #    ns = root.tag.split("}")[0] + "}"
    #else:
    #    ns = ""

    # --- Step 1: Ensure viewBox exists ---
    viewbox = root.attrib.get("viewBox")

    if viewbox is None:
        # Extract width / height (strip units)
        def parse_len(val):
            return float(re.findall(r"[\d.]+", val)[0])

        if "width" not in root.attrib or "height" not in root.attrib:
            raise ValueError("SVG has no viewBox AND no width/height")

        w = parse_len(root.attrib["width"])
        h = parse_len(root.attrib["height"])

        # Create a canonical viewBox
        vb_x, vb_y, vb_w, vb_h = 0.0, 0.0, w, h
    else:
        vb_x, vb_y, vb_w, vb_h = map(float, viewbox.split())

    svg_ratio = vb_w / vb_h

    # --- Step 2: Center crop ---
    if svg_ratio > target_ratio:
        # Too wide → crop width
        new_w = vb_h * target_ratio
        vb_x += (vb_w - new_w) / 2
        vb_w = new_w
    else:
        # Too tall → crop height
        new_h = vb_w / target_ratio
        vb_y += (vb_h - new_h) / 2
        vb_h = new_h

    # --- Step 3: Apply viewBox + scaling ---
    root.attrib["viewBox"] = f"{vb_x} {vb_y} {vb_w} {vb_h}"
    root.attrib["preserveAspectRatio"] = "xMidYMid slice"

    # Remove width/height so viewBox controls scaling
    root.attrib.pop("width", None)
    root.attrib.pop("height", None)

    # --- Write temp SVG ---
    cropped_svg = svg_in.replace(".svg", "_cropped.svg")
    tree.write(cropped_svg)

    # --- Rasterize ---
    cairosvg.svg2png(
        url=cropped_svg,
        write_to=png_out,
        output_width=raster_width,
        output_height=raster_height
    )

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
    #cairosvg.svg2png(
    #    url=svg_path,
    #    write_to="temp.png",
    #    output_width=2000,   # deliberately large
    #    output_height=2000
    #)

    ## Open image and crop from center
    #img = Image.open(png_path)
    #w, h = img.size
    #left   = (w - CROP_WIDTH)  // 2
    #upper  = (h - CROP_HEIGHT) // 2
    #right  = left + CROP_WIDTH
    #lower  = upper + CROP_HEIGHT

    crop_svg_center_no_viewbox(
        svg_in=svg_path,
        png_out=png_path,
        target_ratio=16/10,
        raster_width=512,
        raster_height=320
    )