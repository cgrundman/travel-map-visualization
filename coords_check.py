import pandas as pd
from matplotlib import pyplot as plt
import geopandas as gpd
from shapely.geometry import Point


# LOCATION_CSV = "National_Parks/nps_list.csv"
LOCATION_CSV = "Sehenswuerdigkeiten/sehenswuerdigkeiten.csv"


# CSV into DataFrame
df = pd.read_table(LOCATION_CSV, delimiter =",")
points = df[['longitude', 'latitude']].values

# Combine into GeoDataFrame
points_gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in points])
points_gdf.set_crs(epsg=4326, inplace=True)

# Make list of submaps
submaps = sorted(list(dict.fromkeys(df['designation'].tolist())))

# iterate through submaps
for submap in submaps:
    by_points_gdf = points_gdf[points_gdf['designation'] == f'{submap}']

    # Path to the folder containing shapefiles
    shapefile_dir = "Sehenswuerdigkeiten/geoboundaries_states/"  # adjust as needed

    # Load state GeoDataFrame
    submap_shp = gpd.read_file(f"Sehenswuerdigkeiten/geoboundaries_states/{submap}.shp")
    submap_shp = submap_shp[submap_shp["shapeISO"] == f"DE-{submap}"]  # if using geoBoundaries
    submap_shp = submap_shp.to_crs("EPSG:4326")  # or other projected CRS

    fig, ax = plt.subplots(figsize=(10, 15))

    submap_shp.plot(ax=plt.gca(), edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)

    by_points_gdf.plot(ax=ax, edgecolor="red", color="red", alpha=0.8)

    plt.title("All German States")
    plt.axis("off")
    plt.savefig(f"./plots/temp/{submap}.png")