import geopandas as gpd
import os

# Load shapefile
gdf = gpd.read_file("ir/submaps/geoBoundaries-IRN-ADM1_simplified.shp")

# Create a directory for output shapefiles
output_dir = "ir/submaps"
os.makedirs(output_dir, exist_ok=True)

#gdf.xs(30)['shapeISO'] = 'IR-07'

# Group by state name and export each as its own shapefile
for state_name in gdf["shapeName"].unique():
    if not gdf["shapeName"]:
        gdf["shapeName"]='IR-07'
    state_gdf = gdf[gdf["shapeName"] == state_name]
    filename = os.path.join(output_dir, f"{state_name.replace(' ', '_').replace('US-', '')}.shp")
    state_gdf.to_file(filename)
    print(f"Exported: {filename}")

#filename = os.path.join(output_dir, ".shp")
#gdf.to_file(filename)
#print(f"Exported: {filename}")