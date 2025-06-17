# Import pandas, numpy, and matplotlib
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
# Import Geopandas modules
import geopandas as gpd
# import geoplot
# Import shapely to convert string lat-longs to Point objects
from shapely.geometry import Point, Polygon, LineString, MultiPolygon
from shapely.ops import unary_union, polygonize
# import make_gif
import os
from scipy.spatial import Voronoi
from collections import defaultdict
from PIL import Image


# # Set global variables, directories for map creation and site locations
SCALE = 1

# # National Park Data
# # MAP_NAME = "national_parks"
# # EXTENT=[-120, 25, -73, 49]
# # CENTRAL_LONGITUDE=-98
# # CENTRAL_LATITUDE=39.5
# # LOCATION_CSV = "National_Parks/nps_list.csv"
# # GEO_DATA_DIR = "National_Parks/cb_2018_us_nation_5m/cb_2018_us_nation_5m.shp"
# # COLOR_VALUES = [0.56,.21,0.26] # [unvisited,visited-active,visited-inactive]
# # FIG_SIZE = (20,14)

# Germany Sites
PATH = "Sehenswuerdigkeiten/"
CROP_HEIGHT = 200  # define crop 
# COLOR_VALUES = [0.51,.61,0.66] # [unvisited,visited-active,visited-inactive]

# Meta-Data CSV into list
md = pd.read_table(PATH + 'meta_data.csv', delimiter =",")

# Make List of Submap Names
submaps = list(md['name'])

# Define Map Colors
color_list = list(md['color'])
cmap = mpl.colormaps['tab20b']
colors = cmap(color_list, len(color_list))

# CSV into GeoDataFrame
df = pd.read_table(PATH + 'locations.csv', delimiter =",")
points = df[['longitude', 'latitude']].values
points_gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in points])
points_gdf.set_crs(epsg=4326, inplace=True)

# Initiate Plot
fig, ax = plt.subplots(figsize=(12*SCALE, 18*SCALE))
fig.patch.set_facecolor('#3C4048')

# iterate through submaps
for i, submap in enumerate(submaps):
    submap_points_gdf = points_gdf[points_gdf['submap'] == f'{submap}']

    points_coords = np.array([
        (point.x, point.y) for point in submap_points_gdf.geometry
    ])

    # Path to the folder containing shapefiles
    shapefile_dir = "Sehenswuerdigkeiten/submaps/"  # adjust as needed

    # Load state GeoDataFrame (e.g., Bayern)
    submap_gdf = gpd.read_file(f"Sehenswuerdigkeiten/submaps/{submap}.shp")
    submap_gdf = submap_gdf[submap_gdf["shapeISO"] == f"DE-{submap}"] # if using geoBoundaries
    submap_gdf = submap_gdf.to_crs("EPSG:4326") # or other projected CRS

    # List all .shp files
    # shapefiles = [os.path.join(shapefile_dir, f) for f in os.listdir(shapefile_dir) if f.endswith(".shp")]

    # fig, ax = plt.subplots(figsize=(10, 15))

    # Plot Overall Map
    # main_gdf.plot(ax=plt.gca(), edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)
    
    # Plot outside region
    # bayern_bounding_region.plot(ax=plt.gca(), facecolor='lightblue', edgecolor='blue', alpha=0.5)

    # Plot Region Border
    # bayern.plot(ax=plt.gca(), edgecolor="black", linewidth=1, color=colors[i], alpha=1)

    # Plot points of interest in region
    # by_points_gdf.plot(ax=plt.gca(), edgecolor="darkgoldenrod", color="gold", markersize=15, alpha=1)

    # Plot current submap
    # plt.title(f"{submap}")
    # plt.axis("off")
    # plt.savefig(f"./plots/temp/{submap}.png")
    # plt.show()

    submap_gdf.plot(ax=plt.gca(), edgecolor="black", linewidth=1, color=colors[i], alpha=1)

# Plot Points
# Create a mask for points with and without a date
has_date = points_gdf['date'].notnull()
no_date = points_gdf['date'].isnull()
# Plot points not visited
points_gdf[no_date].plot(ax=plt.gca(), 
                         edgecolor="darkred", 
                         color="red", 
                         linewidth=1*SCALE, 
                         markersize=100*SCALE, 
                         alpha=1)
# Plot points visited
points_gdf[has_date].plot(ax=plt.gca(), 
                          edgecolor="darkgoldenrod", 
                          color="gold", 
                          linewidth=1*SCALE, 
                          markersize=100*SCALE, 
                          alpha=1)

# Plot Location Names
row, column = 0, 0
for index, location in enumerate(points_gdf['name']):
    plt.text(4.1 + 1.59*column, 47 - 0.074*row , location, fontsize=5.5*SCALE, color='#EAEAEA')
    row += 1
    if row % 26 == 0:
        column += 1
        row = 0
    
# Plot all states
plt.title("Deutschland", fontsize=25*SCALE, color='#EAEAEA')
plt.axis("off")
plt.savefig(f"./plots/temp/de.png")
print("Figure created.")
# plt.show()

# Resize Plot
image = Image.open('./plots/temp/de.png') # load the image
width, height = image.size # pull image size
crop_box = (0, CROP_HEIGHT*SCALE, width, height)  # x1, y1, x2, y2
cropped_image = image.crop(crop_box) # crop image
cropped_image.save('./plots/temp/de.png') # save

# Create gif from produced plots
# # make_gif.create_gif(input_folder='./plots/temp', output_gif=f"./gifs/{MAP_NAME}.gif", duration=200)
