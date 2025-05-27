# Import required libraries
import pandas as pd                          # For handling tabular data
from matplotlib import pyplot as plt         # For plotting
import geopandas as gpd                      # For working with geospatial data
from shapely.geometry import Point           # For creating geometric points

# Path to CSV file containing location data
# LOCATION_CSV = "National_Parks/nps_list.csv"  # Alternative path (commented out)
LOCATION_CSV = "Sehenswuerdigkeiten/sehenswuerdigkeiten.csv"  # Main path used

# Load CSV into a Pandas DataFrame
df = pd.read_table(LOCATION_CSV, delimiter=",")  # Read CSV with comma as delimiter

# Extract coordinates from DataFrame
points = df[['longitude', 'latitude']].values  # Numpy array of coordinate pairs

# Create GeoDataFrame with geometric Point objects
points_gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in points])
points_gdf.set_crs(epsg=4326, inplace=True)  # Set coordinate reference system to WGS 84

# Get a list of unique "designation" values (e.g., German state codes)
submaps = sorted(list(dict.fromkeys(df['designation'].tolist())))

# Loop over each unique designation to generate a map
for submap in submaps:
    # Filter points belonging to the current designation (state)
    by_points_gdf = points_gdf[points_gdf['designation'] == f'{submap}']

    # Path to the folder containing shapefiles
    shapefile_dir = "Sehenswuerdigkeiten/geoboundaries_states/"  # Adjust as needed

    # Load shapefile for the current state (must match state code)
    submap_shp = gpd.read_file(f"{shapefile_dir}{submap}.shp")

    # Filter to match exact region (for geoBoundaries naming like "DE-BW", "DE-BY", etc.)
    submap_shp = submap_shp[submap_shp["shapeISO"] == f"DE-{submap}"]

    # Ensure shapefile is in the same CRS as the points
    submap_shp = submap_shp.to_crs("EPSG:4326")

    # Create a plot
    fig, ax = plt.subplots(figsize=(10, 15))

    # Plot the shapefile with transparency and border color
    submap_shp.plot(ax=ax, edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)

    # Plot the corresponding points in red
    by_points_gdf.plot(ax=ax, edgecolor="red", color="red", alpha=0.8)

    # Set plot title and remove axis
    plt.title("All German States")
    plt.axis("off")

    # Save the plot as a PNG file
    plt.savefig(f"./plots/temp/{submap}.png")
