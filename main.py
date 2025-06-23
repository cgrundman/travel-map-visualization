import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
# import make_gif
import os
from PIL import Image


# Set global variables, directories for map creation and site locations
SCALE = 1

# # US National Park Global Variables
# # MAP_NAME = "national_parks"
# # EXTENT=[-120, 25, -73, 49]
# # CENTRAL_LONGITUDE=-98
# # CENTRAL_LATITUDE=39.5
# # LOCATION_CSV = "National_Parks/nps_list.csv"
# # GEO_DATA_DIR = "National_Parks/cb_2018_us_nation_5m/cb_2018_us_nation_5m.shp"
# # COLOR_VALUES = [0.56,.21,0.26] # [unvisited,visited-active,visited-inactive]
# # FIG_SIZE = (20,14)

# Germany Global Variables
PATH = "de"
# COLOR_VALUES = [0.51,.61,0.66] # [unvisited,visited-active,visited-inactive]

# Meta-Data CSV into list
md = pd.read_table(PATH + '/meta_data.csv', delimiter =",")

# Make List of Submap Names
submaps = list(md['name'])

# Define Map Colors
color_list = list(md['color']*0.2 + 0.3)
# cmap = mpl.colormaps['tab20b']
cmap = mpl.colormaps['copper']
colors = cmap(color_list, len(color_list))

# CSV into GeoDataFrame
df = pd.read_table(PATH + '/locations.csv', delimiter =",")
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d', errors='coerce')
df = df.sort_values('date')
points = df[['longitude', 'latitude']].values
points_gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in points])
points_gdf.set_crs(epsg=4326, inplace=True)

counter = 0
# Iterate through dates
for index, row in points_gdf.iterrows():
    # print(points_gdf)

    # Add current date for plot
    current_date = row['date']

    # Activate Current Location
    points_gdf.at[index, 'value'] = 1.0

    if pd.isna(row['date']):
        pass
    else:
        if row['date']:
            print(str(row['date']) + " - " + str(row['value']) + " - " + row['name'])
        # Initialize Plot
        fig, ax = plt.subplots(figsize=(12*SCALE, 18*SCALE))
        fig.patch.set_facecolor('#3C4048')

        # Plot each Submap
        for i, submap in enumerate(submaps):
            submap_points_gdf = points_gdf[points_gdf['submap'] == f'{submap}']

            points_coords = np.array([
                (point.x, point.y) for point in submap_points_gdf.geometry
            ])

            # Path to submap shapefiles
            shapefile_dir = PATH + '/submaps/'

            # Load submap
            submap_gdf = gpd.read_file(shapefile_dir + submap + ".shp")
            submap_gdf = submap_gdf[submap_gdf["shapeISO"] == f"DE-{submap}"]
            submap_gdf = submap_gdf.to_crs("EPSG:4326")

            # Plot submap
            submap_gdf.plot(ax=plt.gca(), edgecolor="black", linewidth=1, color=colors[i], alpha=1)

        # Plot All Points
        points_gdf.plot(
            ax=plt.gca(), 
            edgecolor="darkgoldenrod", 
            color="red", 
            linewidth=0, 
            markersize=75*(SCALE*SCALE), 
            alpha=1
        )
        
        # Plot Points Not Visited
        not_visited = points_gdf['value'] == 0.0 # mask for points without date
        points_gdf[not_visited].plot(
            ax=plt.gca(), 
            edgecolor="darkgoldenrod", 
            color="gold", 
            linewidth=0, 
            markersize=100*(SCALE*SCALE), 
            alpha=1
        )
        
        # Plot Points Visited (Inactive)
        #visited_inactive = points_gdf['value'] == 0.5 # mask for points with date
        #points_gdf[visited_inactive].plot(
        #    ax=plt.gca(), 
        #    edgecolor="darkgoldenrod",
        #    color="gold", 
        #    linewidth=1, 
        #    markersize=75*(SCALE*SCALE), 
        #    alpha=1
        #)

        # Plot Points Visited (Active)
        #visited_active = points_gdf['value'] == 1.0 # mask for points with date
        #points_gdf[visited_active].plot(
        #    ax=plt.gca(), 
        #    edgecolor="darkgoldenrod",
        #    color="green", 
        #    linewidth=0, 
        #    markersize=200*(SCALE*SCALE), 
        #    alpha=1
        #)

        # Plot Location Names
        row, column = 0, 0
        for index, location in enumerate(points_gdf['name']):
            plt.text(4.1 + 1.59*column, 47 - 0.074*row , location, fontsize=5.5*SCALE, color='#EAEAEA')
            row += 1
            if row % 26 == 0:
                column += 1
                row = 0
            
        # Add Plot Data and Save
        plt.title("Deutschland", fontsize=25*SCALE, color='#EAEAEA')
        plt.axis("off")
        plt.savefig(f"./plots/temp/{PATH}_{current_date}.png")
        # print("Figure created.")
        # plt.show()

        # points_gdf.at[index, 'value'] = 0.5

        # Resize Plot
        with Image.open(f'./plots/temp/{PATH}_{current_date}.png') as image: # load the image
            width, height = image.size # pull image size
            crop_borders = list(md['cropping'])[0:8]
            if SCALE < 3:
                x1, y1, x2, y2 = crop_borders[0:4]
            else:
                x1, y1, x2, y2 = crop_borders[-4:]
            crop_box = (width*x1, height*y1, width*x2, height*y2)
            cropped_image = image.crop(crop_box) # crop image
            cropped_image.save(f'./plots/temp/{PATH}_{current_date}.png') # save
            # print("Figure cropped.")

        plt.close(fig)

        counter += 1
        print(counter)

    # Update Current Date into Old Date 
    old_date = current_date

# Create gif from produced plots
# # make_gif.create_gif(input_folder='./plots/temp', output_gif=f"./gifs/{MAP_NAME}.gif", duration=200)

# Clean temp directory
