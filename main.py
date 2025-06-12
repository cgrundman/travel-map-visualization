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
# MAP_NAME = "germany_sites"
# EXTENT=[6, 47, 15, 55]
# CENTRAL_LONGITUDE=10.5
# CENTRAL_LATITUDE=51
LOCATION_CSV = "Sehenswuerdigkeiten/sehenswuerdigkeiten.csv"
SUBMAPS = ['BB', 'BE', 'BW', 'BY', 'HB', 'HE', 'HH', 'MV', 'NI', 'NW', 'RP', 'SH', 'SL', 'SN', 'ST', 'TH']
COLORS = [0.6, 0.4, 0.0, 0.4, 0.0, 0.2, 0.8, 0.2, 0.4, 0.6, 0.8, 0.0, 0.4, 0.2, 0.8, 0.0]
# GEO_DATA_DIR = "Sehenswuerdigkeiten/geoBoundaries-DEU-ADM1-all/geoBoundaries-DEU-ADM1_simplified.shp" # "Sehenswuerdigkeiten/Germany_Boundary/germany_Germany_Country_Boundary.shp"
# COLOR_VALUES = [0.51,.61,0.66] # [unvisited,visited-active,visited-inactive]
# FIG_SIZE = (14,18)

def augment_points(points, bounds):
    minx, miny, maxx, maxy = bounds.values[0]

    buffer = 1 * max(maxx - minx, maxy - miny)
    minx -= buffer
    miny -= buffer
    maxx += buffer
    maxy += buffer

    # Perimeter points
    perimeter_points = [
        Point(minx, miny),
        Point(minx, maxy),
        Point(maxx, miny),
        Point(maxx, maxy),
        Point((minx + maxx)/2, miny),
        Point((minx + maxx)/2, maxy),
        Point(minx, (miny + maxy)/2),
        Point(maxx, (miny + maxy)/2)
    ]

    # Create a list of dicts for perimeter metadata
    perimeter_data = []

    for idx, point in enumerate(perimeter_points):
        perimeter_data.append({
            'number': 300 + idx,    # or just idx
            'name': 'Perimeter',
            'designation': None,
            'latitude': point[0],
            'longitude': point[1],
        })

    # Convert to GeoDataFrame
    perimeter_gdf = gpd.GeoDataFrame(perimeter_data, geometry='geometry', crs=points.crs)

    # Combine with your real points
    # original_points = [Point(x, y) for x, y in zip(x_coords, y_coords)]
    all_points = pd.concat([points, perimeter_gdf], ignore_index=True)

    return all_points


def max_bounds(bounds):

    # Define the corner points of the rectangle
    bounding_box_coords = [
        (bounds.minx, bounds.miny),  # lower left
        (bounds.minx, bounds.maxy),  # upper left
        (bounds.maxx, bounds.maxy),  # upper right
        (bounds.maxx, bounds.miny),  # lower right
        (bounds.minx, bounds.miny)   # close the polygon
    ]

    # Create the polygon
    bounding_box_polygon = Polygon(bounding_box_coords)

    gdf = gpd.GeoDataFrame(geometry=[bounding_box_polygon])

    return gdf


def voronoi_polygons(vor, bbox):
    """
    vor: scipy.spatial.Voronoi object
    bbox: shapely Polygon representing the bounding box
    """
    lines = []
    center = vor.points.mean(axis=0)
    radius = 1000  # a large number to ensure the lines extend far enough

    # Loop through ridges
    for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
        simplex = np.asarray(simplex)
        if np.all(simplex >= 0):
            # Finite ridge: get the segment
            lines.append(LineString(vor.vertices[simplex]))
        else:
            # Infinite ridge: compute the direction and extend it
            i, j = pointidx
            p0 = vor.points[i]
            p1 = vor.points[j]
            # Midpoint
            midpoint = (p0 + p1) / 2
            # Direction perpendicular to the line between p0 and p1
            direction = np.array([p1[1] - p0[1], -(p1[0] - p0[0])])
            direction = direction / np.linalg.norm(direction)
            # Extend the line
            far_point = midpoint + direction * radius
            segment = LineString([midpoint, far_point])
            lines.append(segment)

    # Polygonize lines
    polygons = list(polygonize(lines))

    # Clip with bounding box
    clipped_polygons = [poly.intersection(bbox) for poly in polygons]

    return clipped_polygons


# CSV into DataFrame
df = pd.read_table(LOCATION_CSV, delimiter =",")
# filtered_rows = df[df['designation'] == 'BY']
points = df[['longitude', 'latitude']].values

# Combine into GeoDataFrame
# voronoi_gdf = gpd.GeoDataFrame(geometry=polygons)
points_gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in points])
points_gdf.set_crs(epsg=4326, inplace=True)

# Path for main outline
#main_shp = "Sehenswuerdigkeiten/geoBoundaries-DEU-ADM1-all/geoBoundaries-DEU-ADM0.shp"
# main_gdf = gpd.read_file(main_shp)

# Make list of submaps
# submaps = ['BB', 'BE', 'BW', 'BY', 'HB', 'HE', 'HH', 'MV', 'NI', 'NW', 'RP', 'SH', 'SL', 'SN', 'ST', 'TH']

cmap = mpl.colormaps['tab20b']
colors = cmap(COLORS, len(SUBMAPS))
# submaps = ['BB']

fig, ax = plt.subplots(figsize=(12, 18))

# main_gdf.plot(ax=plt.gca(), edgecolor="black", linewidth=4, alpha=1)

# iterate through submaps
for i, submap in enumerate(SUBMAPS):
    # Extract only the points for Bavaria
    # by_points_gdf = points_gdf[points_gdf['designation'] == 'BY']
    by_points_gdf = points_gdf[points_gdf['submap'] == f'{submap}']

    points_coords = np.array([
        (point.x, point.y) for point in by_points_gdf.geometry
    ])

    # Path to the folder containing shapefiles
    shapefile_dir = "Sehenswuerdigkeiten/geoboundaries_states/"  # adjust as needed

    # Load state GeoDataFrame (e.g., Bayern)
    bayern = gpd.read_file(f"Sehenswuerdigkeiten/geoboundaries_states/{submap}.shp")
    bayern = bayern[bayern["shapeISO"] == f"DE-{submap}"]  # if using geoBoundaries
    bayern = bayern.to_crs("EPSG:4326")  # or other projected CRS

    bayern_bounds = bayern.geometry.bounds

    '''

    # Augment points
    all_points = augment_points(by_points_gdf, bayern_bounds)

    bayern_bounding_region = max_bounds(bayern_bounds)

    # if len(points_coords) >= 4:
    vor = Voronoi(all_points)
        # proceed with Voronoi analysis
    # else:
        # print("Not enough points to compute a Voronoi diagram.")

    # Create Voronoi diagram within Bavaria
    bbox_polygon = bayern_bounding_region.iloc[0].geometry

    voronoi_cells = voronoi_polygons(vor, bbox_polygon)
    voronoi_gdf = gpd.GeoDataFrame(geometry=voronoi_cells)
    # print([poly.is_empty for poly in voronoi_gdf])
    # bayern_voronoi_clipped = make_voronoi_for_state(bayern, by_points_gdf)
    # bayern_voronoi_clipped = make_voronoi_for_state(points_gdf)

    '''

    # List all .shp files
    # shapefiles = [os.path.join(shapefile_dir, f) for f in os.listdir(shapefile_dir) if f.endswith(".shp")]

    # fig, ax = plt.subplots(figsize=(10, 15))

    # Plot Overall Map
    # main_gdf.plot(ax=plt.gca(), edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)
    
    # Plot outside region
    # bayern_bounding_region.plot(ax=plt.gca(), facecolor='lightblue', edgecolor='blue', alpha=0.5)

    # Plot Region Border
    # bayern_voronoi_clipped.plot(ax=plt.gca(), edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)
    bayern.plot(ax=plt.gca(), edgecolor="black", linewidth=1, color=colors[i], alpha=1)

    # Plot points of interest in region
    # by_points_gdf.plot(ax=plt.gca(), edgecolor="darkgoldenrod", color="gold", markersize=15, alpha=1)

    # voronoi_gdf.plot(ax=plt.gca(), cmap='tab20', alpha=0.4, edgecolor='grey')

    # Plot current submap
    # plt.title(f"{submap}")
    # plt.axis("off")
    # plt.savefig(f"./plots/temp/{submap}.png")
    # plt.show()

points_gdf.plot(ax=plt.gca(), edgecolor="darkgoldenrod", color="gold", markersize=50, alpha=1)

loc_names = points_gdf['name'].tolist()
row, column = 0, 0
for i, location in enumerate(loc_names):
    plt.text(4.1 + 1.59*column, 47 - 0.074*row , loc_names[i], fontsize=5.5, color='black')
    row += 1
    if row % 26 == 0:
        column += 1
        row = 0
    

# Plot all states
plt.title("Deutschland", fontsize=25)
plt.axis("off")
plt.savefig(f"./plots/temp/de.png")
print("Figure created.")
# plt.show()

# Resize Plot
image = Image.open('./plots/temp/de.png') # load the image
crop_height = 200  # define crop 
width, height = image.size # pull image size
crop_box = (0, crop_height, width, height)  # x1, y1, x2, y2
cropped_image = image.crop(crop_box) # crop image
cropped_image.save('./plots/temp/de.png') # save

# Create gif from produced plots
# # make_gif.create_gif(input_folder='./plots/temp', output_gif=f"./gifs/{MAP_NAME}.gif", duration=200)
