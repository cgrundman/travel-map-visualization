import geopandas as gpd
import os
#import json

IMPORT_PATH = "masters/global/"
EXPORT_PATH = "masters/SubMaps_ADM1/"
file_path = "geoBoundariesCGAZ_ADM1.shp"

# Load shapefile
gdf = gpd.read_file(IMPORT_PATH + file_path)

# Create a directory for output shapefiles
os.makedirs(EXPORT_PATH, exist_ok=True)

#with open(f"{PATH}/map_translate.json", "r") as f:
#    states_translate = json.load(f)

# Group by state name and export each as its own shapefile
for state_name in gdf["shapeName"].unique():
    state_gdf = gdf[gdf["shapeName"] == state_name]
    filename = os.path.join(EXPORT_PATH, f"{state_name}.shp")
    state_gdf.to_file(filename)
    print(f"Exported: {filename}")

#filename = os.path.join(output_dir, ".shp")
#gdf.to_file(filename)
#print(f"Exported: {filename}")
