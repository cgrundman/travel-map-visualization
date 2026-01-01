import geopandas as gpd
import os
import json

# Load shapefile
gdf = gpd.read_file("ir/submaps/geoBoundaries-IRN-ADM1_simplified.shp")

# Create a directory for output shapefiles
output_dir = "ir/submaps"
os.makedirs(output_dir, exist_ok=True)

with open("ir/submaps/map_translate.json", "r") as f:
    states_translate = json.load(f)

# Group by state name and export each as its own shapefile
for state_name in gdf["shapeName"].unique():
    state_gdf = gdf[gdf["shapeName"] == state_name]
    filename = os.path.join(output_dir, f"{states_translate[state_name]}.shp")
    state_gdf.to_file(filename)
    print(f"Exported: {filename}")

#filename = os.path.join(output_dir, ".shp")
#gdf.to_file(filename)
#print(f"Exported: {filename}")