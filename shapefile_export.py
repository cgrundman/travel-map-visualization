import geopandas as gpd
import os

# Load shapefile
gdf = gpd.read_file("us/submaps/geoBoundaries-USA-ADM1-all/geoBoundaries-USA-ADM1_simplified.shp")

# Create a directory for output shapefiles
output_dir = "us/submaps"
os.makedirs(output_dir, exist_ok=True)

# Group by state name and export each as its own shapefile
for state_name in gdf["shapeISO"].unique():
    state_gdf = gdf[gdf["shapeISO"] == state_name]
    filename = os.path.join(output_dir, f"{state_name.replace(' ', '_').replace('US-', '')}.shp")
    state_gdf.to_file(filename)
    print(f"Exported: {filename}")

#filename = os.path.join(output_dir, ".shp")
#gdf.to_file(filename)
#print(f"Exported: {filename}")