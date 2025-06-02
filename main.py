# Import pandas, numpy, and matplotlib
import pandas as pd
from matplotlib import pyplot as plt
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

# # Germany Sites
# MAP_NAME = "germany_sites"
# EXTENT=[6, 47, 15, 55]
# CENTRAL_LONGITUDE=10.5
# CENTRAL_LATITUDE=51
LOCATION_CSV = "Sehenswuerdigkeiten/sehenswuerdigkeiten.csv"
# GEO_DATA_DIR = "Sehenswuerdigkeiten/geoBoundaries-DEU-ADM1-all/geoBoundaries-DEU-ADM1_simplified.shp" # "Sehenswuerdigkeiten/Germany_Boundary/germany_Germany_Country_Boundary.shp"
# COLOR_VALUES = [0.51,.61,0.66] # [unvisited,visited-active,visited-inactive]
# FIG_SIZE = (14,18)


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

# Make list of submaps
submaps = ['BB', 'BE', 'BW', 'BY', 'HB', 'HE', 'HH', 'MV', 'NI', 'NW', 'RP', 'SH', 'SL', 'SN', 'ST', 'TH']

# iterate through submaps
for submap in submaps:
    # Extract only the points for Bavaria
    # by_points_gdf = points_gdf[points_gdf['designation'] == 'BY']
    by_points_gdf = points_gdf[points_gdf['designation'] == f'{submap}']

    points_coords = np.array([
        (point.x, point.y) for point in by_points_gdf.geometry
    ])

    if len(points_coords) >= 4:
        vor = Voronoi(points_coords)
        # proceed with Voronoi analysis
    else:
        print("Not enough points to compute a Voronoi diagram.")

    # Path for main outline
    main_shp = "Sehenswuerdigkeiten/geoBoundaries-DEU-ADM1-all/geoBoundaries-DEU-ADM0.shp"
    main_gdf = gpd.read_file(main_shp)

    # Path to the folder containing shapefiles
    shapefile_dir = "Sehenswuerdigkeiten/geoboundaries_states/"  # adjust as needed

    # Load state GeoDataFrame (e.g., Bayern)
    bayern = gpd.read_file(f"Sehenswuerdigkeiten/geoboundaries_states/{submap}.shp")
    bayern = bayern[bayern["shapeISO"] == f"DE-{submap}"]  # if using geoBoundaries
    bayern = bayern.to_crs("EPSG:4326")  # or other projected CRS

    bayern_bounds = bayern.geometry.bounds

    bayern_bounding_region = max_bounds(bayern_bounds)

    # Create Voronoi diagram within Bavaria
    bbox_polygon = bayern_bounding_region.iloc[0].geometry

    voronoi_cells = voronoi_polygons(vor, bbox_polygon)
    voronoi_gdf = gpd.GeoDataFrame(geometry=voronoi_cells)
    # print([poly.is_empty for poly in voronoi_gdf])
    # bayern_voronoi_clipped = make_voronoi_for_state(bayern, by_points_gdf)
    # bayern_voronoi_clipped = make_voronoi_for_state(points_gdf)

    # List all .shp files
    # shapefiles = [os.path.join(shapefile_dir, f) for f in os.listdir(shapefile_dir) if f.endswith(".shp")]

    fig, ax = plt.subplots(figsize=(10, 15))

    # Plot Overall Map
    # main_gdf.plot(ax=plt.gca(), edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)
    
    # Plot outside region
    bayern_bounding_region.plot(facecolor='lightblue', edgecolor='blue', alpha=0.5)

    # Plot Region Border
    # bayern_voronoi_clipped.plot(ax=plt.gca(), edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)
    bayern.plot(ax=plt.gca(), edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)

    # Plot points of interest in region
    by_points_gdf.plot(ax=plt.gca(), edgecolor="red", color="red", alpha=0.5)

    # voronoi_gdf.plot(ax=ax, cmap='tab20', alpha=0.4, edgecolor='grey')

    plt.title("All German States")
    plt.axis("off")
    plt.savefig(f"./plots/temp/{submap}.png")
    # plt.show()

# Create gif from produced plots
# # make_gif.create_gif(input_folder='./plots/temp', output_gif=f"./gifs/{MAP_NAME}.gif", duration=200)