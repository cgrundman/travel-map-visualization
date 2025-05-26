# Import pandas, numpy, and matplotlib
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
# Import Geopandas modules
import geopandas as gpd
import geoplot
# Import shapely to convert string lat-longs to Point objects
from shapely.geometry import Point, Polygon
# import make_gif
import os
from scipy.spatial import Voronoi


def voronoi_regions(vor, radius=1000):
    from collections import defaultdict

    new_regions = []
    new_vertices = vor.vertices.tolist()
    center = vor.points.mean(axis=0)

    # Map ridge vertices to all ridges for a point
    all_ridges = defaultdict(list)
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges[p1].append((p2, v1, v2))
        all_ridges[p2].append((p1, v1, v2))

    # Construct new regions
    for p1, region_idx in enumerate(vor.point_region):
        region = vor.regions[region_idx]
        if all(v >= 0 for v in region):
            new_regions.append([vor.vertices[i] for i in region])
            continue

        # Reconstruct non-finite region
        ridges = all_ridges[p1]
        new_region = [vor.vertices[v] for v in region if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                continue

            # Calculate direction and extend
            t = vor.points[p2] - vor.points[p1]
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])
            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius
            new_region.append(far_point.tolist())

        new_regions.append(new_region)

    return [Polygon(r) for r in new_regions if len(r) > 2]


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

# def plot_voronoi(counter, geodf, basemap, projection, site):
#     # Setup the Voronoi axes; this creates the Voronoi regions
#     ax = geoplot.voronoi(
#         geodf, # Define the GeoPandas DataFrame
#         figsize=FIG_SIZE, # Define resolution of figure
#         hue='values', # df column used to color regions
#         clip=basemap,  # Define the voronoi clipping (map edge)
#         projection=projection, # Define the Projection
#         cmap='tab20b', # color set
#         # k=None, # No. of discretized buckets to create
#         legend=False, # Dont create a legend
#         edgecolor='#000000', # Color of the voronoi boundaries
#         linewidth=1 # width of the voronoi boundary lines
#     )

#     # Render the plot with a base map
#     geoplot.polyplot(
#         basemap,  # Base Map
#         ax=ax,  # Axis attribute we created above
#         extent=EXTENT, # Set plotting boundaries to base map boundaries
#         edgecolor='black',  # Color of base map's edges
#         linewidth=3,  # Width of base map's edge lines
#         zorder=0.5  # Plot base map edges above the voronoi regions
#     )
    
#     # Format date
#     date_list = list(map(str, str(site['date'])))
#     year_list, month_list, day_list = date_list[:4], date_list[4:6], date_list[6:] 
#     year = map(str, year_list)
#     year = ''.join(year)
#     month = map(str, month_list)
#     month = ''.join(month)
#     day = map(str, day_list)
#     day = ''.join(day)
#     # year = ''.join(date_list[:4])
#     # if math.isnan(site['designation']):
#     if type(site['designation']) == type(0.0):
#         plt.title(f'{site['name']}, {month}/{day}/{year}', fontsize=36, loc='right')
#     elif type(site['designation']) == type("string"):
#         plt.title(f'{site['name']} {site['designation']}, {month}/{day}/{year}', fontsize=36, loc='right')
#     print(f"Saving plot: {MAP_NAME}_{counter}")
#     plt.savefig(f'plots/temp/{MAP_NAME}_{counter}.png')
#     plt.close()

# CSV into DataFrame
df = pd.read_table(LOCATION_CSV, delimiter =",")
filtered_rows = df[df['designation'] == 'BY']
points = df[['longitude', 'latitude']].values

# # Iterate through sites visited
# for index, row in df.iterrows():
#     df.at[index,'values'] = COLOR_VALUES[0]

# # Add min and max points
# max_row = [len(df),"Max Point","not a point",34.593218347568765,69.17071209340384,1.0,0]
# df.loc[len(df)] = max_row # append to dataframe
# min_row = [len(df),"Min Point","not a point",39.043989815673996,125.76231588440946,0.0,0]
# df.loc[len(df)] = min_row # append to dataframe

# # Sort the dataframe by date
# df = df.sort_values(by=['date'])

# # Import USA data for region clipping
# base_map = geopandas.read_file(GEO_DATA_DIR)
# base_map = base_map[base_map["shapeISO"] == "DE-BY"]

# # Set the map projection
# proj = geoplot.crs.AlbersEqualArea(
#     central_longitude=CENTRAL_LONGITUDE, 
#     central_latitude=CENTRAL_LATITUDE
# )

# # Iterate through sites visited
# counter = 0
# for index, row in df.iterrows():
#     # if not np.isnan(row['date']):
#     if row['date'] != 0:
#         # Set current region to active
#         df.at[index,'values'] = COLOR_VALUES[1]

#         # Convert df to gdf (GeoPandas DataFrame)
#         geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
#         # df['geometry'] = geometry
#         gdf = geopandas.GeoDataFrame(df, geometry=geometry)

#         # Plot the current map state
#         counter += 1
#         # plot_voronoi(counter, geodf=gdf, basemap=base_map, projection=proj, site=row)
#         print(df.at[index,'name'])
        
#         # Set current region to inactive
#         df.at[index,'values'] = COLOR_VALUES[2]

# # Toubleshooting Map
# # print(counter)
# plot_voronoi(counter, geodf=gdf, basemap=base_map, projection=proj, site=row)

# # make_gif.create_gif(input_folder='./plots/temp', output_gif=f"./gifs/{MAP_NAME}.gif", duration=200)


# Compute the Voronoi diagram
vor = Voronoi(points)

# Create Voronoi polygons
polygons = voronoi_regions(vor)

# Combine into GeoDataFrame
voronoi_gdf = gpd.GeoDataFrame(geometry=polygons)
points_gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in points])
points_gdf.set_crs(epsg=4326, inplace=True)

# Path for main outline
main_shp = "Sehenswuerdigkeiten/geoBoundaries-DEU-ADM1-all/geoBoundaries-DEU-ADM0.shp"
main_gdf = gpd.read_file(main_shp)

# Path to the folder containing shapefiles
shapefile_dir = "Sehenswuerdigkeiten/geoboundaries_states/"  # adjust as needed

# List all .shp files
shapefiles = [os.path.join(shapefile_dir, f) for f in os.listdir(shapefile_dir) if f.endswith(".shp")]

# Load each shapefile into a list of GeoDataFrames
gdfs = [gpd.read_file(shp) for shp in shapefiles]

fig, ax = plt.subplots(figsize=(10, 15))

main_gdf.plot(ax=ax, edgecolor="black", alpha=1, linewidth=3)

for gdf in gdfs:
    gdf.plot(ax=ax, edgecolor="black", alpha=0.2,linewidth=1)

points_gdf.plot(ax=ax, edgecolor="red", color="red", alpha=0.8)

plt.title("All German States")
plt.axis("off")
plt.show()