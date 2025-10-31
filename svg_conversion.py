import os
import cairosvg

PATH = "de"

svg_files = [f for f in os.listdir(f"{PATH}/submaps") if f.lower().endswith(".svg")]
for file in svg_files:
    #print(file[:-4])
    cairosvg.svg2png(url=f"{PATH}/submaps/{file}", write_to=f"{PATH}/submaps/{file[:-4]}.png")