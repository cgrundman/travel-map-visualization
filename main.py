# Import pandas, numpy, and matplotlib
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
# Import Geopandas modules
import geopandas as gpd
# import geoplot
# Import shapely to convert string lat-longs to Point objects
from shapely.geometry import Point, Polygon, LineString
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


def voronoi_regions(vor, boundary_polygon):

    new_regions = []
    center = vor.points.mean(axis=0)
    all_ridges = defaultdict(list)

    # Build a mapping from point to its ridges
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges[p1].append((p2, v1, v2))
        all_ridges[p2].append((p1, v1, v2))

    for p1, region_idx in enumerate(vor.point_region):
        region = vor.regions[region_idx]

        # Skip empty or invalid regions
        if len(region) == 0:
            continue

        # If the region is finite, just take its vertices
        if all(v >= 0 for v in region):
            polygon = Polygon([vor.vertices[v] for v in region])
            clipped = polygon.intersection(boundary_polygon)
            if not clipped.is_empty:
                new_regions.append(clipped)
            continue

        # Reconstruct infinite region
        ridges = all_ridges[p1]
        region_coords = []

        for p2, v1, v2 in ridges:
            if v1 >= 0 and v2 >= 0:
                region_coords.append((vor.vertices[v1], vor.vertices[v2]))
            else:
                # Extend infinite ridge until it intersects the boundary
                if v1 == -1:
                    v_finite = vor.vertices[v2]
                else:
                    v_finite = vor.vertices[v1]

                t = vor.points[p2] - vor.points[p1]
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])
                midpoint = vor.points[[p1, p2]].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n

                # Create a far away point in that direction
                far_point = v_finite + direction * 1e5
                region_coords.append((v_finite, far_point))

        # Turn edges into a polygon
        polygon = polygonize(LineString(pair) for pair in region_coords)
        merged = unary_union(list(polygon))
        clipped = merged.intersection(boundary_polygon)

        if not clipped.is_empty:
            new_regions.append(clipped)

    return new_regions


def make_voronoi_for_state(state_gdf, points_gdf):
    """
    Generate and clip Voronoi polygons within a given state.
    
    Args:
        state_gdf (GeoDataFrame or GeoSeries): A GeoDataFrame or GeoSeries with one polygon representing the state.
        points_gdf (GeoDataFrame): A GeoDataFrame with point geometries within the state.
        radius (float): Radius to extend infinite Voronoi edges.

    Returns:
        GeoDataFrame: Clipped Voronoi regions.
    """
    # Ensure both are in the same projected CRS (UTM Zone 32N is typical for Germany)
    projected_crs = "EPSG:4326"
    state_proj = state_gdf.to_crs(projected_crs)
    points_proj = points_gdf.to_crs(projected_crs)

    # Extract point coordinates
    coords = np.array([[geom.x, geom.y] for geom in points_proj.geometry])

    # Compute Voronoi diagram
    vor = Voronoi(coords)
    
    # Create regions
    polygons = voronoi_regions(vor, state_proj)
    voronoi_gdf = gpd.GeoDataFrame(geometry=polygons, crs=projected_crs)

    # Clip Voronoi to the state boundary
    clipped = gpd.overlay(voronoi_gdf, state_proj, how="intersection")

    return clipped


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

    # Path for main outline
    main_shp = "Sehenswuerdigkeiten/geoBoundaries-DEU-ADM1-all/geoBoundaries-DEU-ADM0.shp"
    main_gdf = gpd.read_file(main_shp)

    # Path to the folder containing shapefiles
    shapefile_dir = "Sehenswuerdigkeiten/geoboundaries_states/"  # adjust as needed

    # Load state GeoDataFrame (e.g., Bayern)
    bayern = gpd.read_file(f"Sehenswuerdigkeiten/geoboundaries_states/{submap}.shp")
    bayern = bayern[bayern["shapeISO"] == f"DE-{submap}"]  # if using geoBoundaries
    bayern = bayern.to_crs("EPSG:4326")  # or other projected CRS

    # Create Voronoi diagram within Bavaria
    # bayern_voronoi_clipped = make_voronoi_for_state(bayern, by_points_gdf)
    # bayern_voronoi_clipped = make_voronoi_for_state(bayern, points_gdf)

    # List all .shp files
    # shapefiles = [os.path.join(shapefile_dir, f) for f in os.listdir(shapefile_dir) if f.endswith(".shp")]

    fig, ax = plt.subplots(figsize=(10, 15))

    # main_gdf.plot(ax=ax, edgecolor="black", alpha=1, linewidth=3)
    bayern.plot(ax=plt.gca(), edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)
    # bayern_voronoi_clipped.plot(ax=plt.gca(), edgecolor="black", linewidth=0.5, cmap="tab20b", alpha=0.6)

    by_points_gdf.plot(ax=ax, edgecolor="red", color="red", alpha=0.8)

    plt.title("All German States")
    plt.axis("off")
    plt.savefig(f"./plots/temp/{submap}.png")
    # plt.show()

# Create gif from produced plots
# # make_gif.create_gif(input_folder='./plots/temp', output_gif=f"./gifs/{MAP_NAME}.gif", duration=200)