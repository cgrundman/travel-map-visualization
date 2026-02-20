import geopandas as gpd
import os
#import json

PATH = "false"# "us/submaps/"
file_path = "geoBoundaries-USA-ADM1-all/geoBoundaries-USA-ADM1_simplified.shp"

# Load shapefile
gdf = gpd.read_file(PATH + file_path)

# Create a directory for output shapefiles
os.makedirs(PATH, exist_ok=True)

#with open(f"{PATH}/map_translate.json", "r") as f:
#    states_translate = json.load(f)

# Group by state name and export each as its own shapefile
for state_name in gdf["shapeName"].unique():
    state_gdf = gdf[gdf["shapeName"] == state_name]
    filename = os.path.join(PATH, f"{state_name}.shp")
    state_gdf.to_file(filename)
    print(f"Exported: {filename}")

#filename = os.path.join(output_dir, ".shp")
#gdf.to_file(filename)
#print(f"Exported: {filename}")