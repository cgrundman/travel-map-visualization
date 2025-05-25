import geopandas as gpd
import os

# Load your Germany admin level 1 shapefile
gdf = gpd.read_file("Sehenswuerdigkeiten/geoBoundaries-DEU-ADM1-all/geoBoundaries-DEU-ADM1_simplified.shp")

# Create a directory for output shapefiles
output_dir = "Sehenswuerdigkeiten/geoboundaries_states"
os.makedirs(output_dir, exist_ok=True)

# Group by state name and export each as its own shapefile
for state_name in gdf["shapeISO"].unique():
    state_gdf = gdf[gdf["shapeISO"] == state_name]
    filename = os.path.join(output_dir, f"{state_name.replace(' ', '_').replace('DE-', '')}.shp")
    state_gdf.to_file(filename)
    print(f"Exported: {filename}")
