import geopandas as gpd
import os

# Load shapefile
gdf = gpd.read_file("eu/submaps/Belarus/geoBoundaries-BLR-ADM0_simplified.shp")

# Create a directory for output shapefiles
output_dir = "eu/submaps"
os.makedirs(output_dir, exist_ok=True)

# # Group by state name and export each as its own shapefile
# for state_name in gdf["shapeISO"].unique():
#     state_gdf = gdf[gdf["shapeISO"] == state_name]
#     filename = os.path.join(output_dir, f"{state_name.replace(' ', '_').replace('DE-', '')}.shp")
#     state_gdf.to_file(filename)
#     print(f"Exported: {filename}")

filename = os.path.join(output_dir, "BY.shp")
gdf.to_file(filename)
print(f"Exported: {filename}")