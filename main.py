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
SUBMAPS = [{"name": 'BB', "color": 0.6},
           {"name": 'BE', "color": 0.4},
           {"name": 'BW', "color": 0.0},
           {"name": 'BY', "color": 0.4},
           {"name": 'HB', "color": 0.0},
           {"name": 'HE', "color": 0.2},
           {"name": 'HH', "color": 0.8},
           {"name": 'MV', "color": 0.2},
           {"name": 'NI', "color": 0.4},
           {"name": 'NW', "color": 0.6},
           {"name": 'RP', "color": 0.8},
           {"name": 'SH', "color": 0.0},
           {"name": 'SL', "color": 0.4},
           {"name": 'SN', "color": 0.2},
           {"name": 'ST', "color": 0.8},
           {"name": 'TH', "color": 0.0}]
CROP_HEIGHT = 200  # define crop 
# COLOR_VALUES = [0.51,.61,0.66] # [unvisited,visited-active,visited-inactive]

# CSV into DataFrame
df = pd.read_table(PATH + 'locations.csv', delimiter =",")
points = df[['longitude', 'latitude']].values

# Combine into GeoDataFrame
points_gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in points])
points_gdf.set_crs(epsg=4326, inplace=True)

# Define Map Colors
colors = list(map(lambda d: d.get('color'), filter(lambda d: 'color' in d, SUBMAPS)))
cmap = mpl.colormaps['tab20b']
colors = cmap(colors, len(SUBMAPS))

# Initiate Plot
fig, ax = plt.subplots(figsize=(12*SCALE, 18*SCALE))
fig.patch.set_facecolor('#3C4048')

# main_gdf.plot(ax=plt.gca(), edgecolor="black", linewidth=4, alpha=1)

# iterate through submaps
for i, submap in enumerate(SUBMAPS):
    submap_points_gdf = points_gdf[points_gdf['submap'] == f'{submap['name']}']

    points_coords = np.array([
        (point.x, point.y) for point in submap_points_gdf.geometry
    ])

    # Path to the folder containing shapefiles
    shapefile_dir = "Sehenswuerdigkeiten/geoboundaries_states/"  # adjust as needed

    # Load state GeoDataFrame (e.g., Bayern)
    submap_gdf = gpd.read_file(f"Sehenswuerdigkeiten/geoboundaries_states/{submap['name']}.shp")
    submap_gdf = submap_gdf[submap_gdf["shapeISO"] == f"DE-{submap['name']}"]  # if using geoBoundaries
    submap_gdf = submap_gdf.to_crs("EPSG:4326")  # or other projected CRS

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
