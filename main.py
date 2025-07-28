import pandas as pd
import json
from matplotlib import pyplot as plt
# import matplotlib as mpl
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import make_gif
import os
from PIL import Image

from colormap import custom_cmap


# Set global variables, directories for map creation and site locations
SCALE = 1

# US National Park Global Variables
#PATH = "us"

# Germany Global Variables
#PATH = "de"

# Europe Global Variables
PATH = "eu"

# Load the JSON Meta-Data
with open(PATH + '/meta_data.json', 'r') as f:
    meta_data = json.load(f)

# Access Meta-Data variables
title = meta_data["Title"]
fig_size = meta_data["Figure Size"]
crop_s = meta_data["Cropping"]["small"]
crop_l = meta_data["Cropping"]["large"]
color_unvisited = meta_data["Colors"]["unvisited"]
color_active = meta_data["Colors"]["active"]
color_visited = meta_data["Colors"]["visited"]
marker_size = meta_data["Marker Size"]
labels = meta_data["Labels"]

# Make List of Submap Names
submap_files = os.listdir(PATH + '/submaps/')
submaps = [submap.replace('.shp', '') for submap in submap_files if '.shp' in submap]
submaps.sort()

# CSV into GeoDataFrame
df = pd.read_table(PATH + '/locations.csv', delimiter =",")
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d', errors='coerce')
df_sorted = df.sort_values('date')
points = df_sorted[['longitude', 'latitude']].values
points_gdf = gpd.GeoDataFrame(df_sorted, geometry=[Point(xy) for xy in points])
points_gdf.set_crs(epsg=4326, inplace=True)

# Create initial old date
old_date = '1875-01-01 00:00:00'

# Iterate through dates
for index, row in points_gdf.iterrows():

    # Add current date for plot
    current_date = row['date']

    if old_date != current_date:

        if pd.isna(row['date']):
            pass
        else:
            if row['date']:
                print(str(row['date']) + " - " + row['name'])
            # Initialize Plot
            fig, ax = plt.subplots(figsize=(fig_size[0]*SCALE, fig_size[1]*SCALE))
            fig.patch.set_facecolor('#3C4048')

            # Plot each Submap
            for i, submap in enumerate(submaps):
                submap_points_gdf = points_gdf[points_gdf['submap'] == submap]

                # Count how many dates are less than current date
                num_past_dates = (submap_points_gdf['date'] < current_date).sum()

                # Calculate the ratio and associated color
                ratio = num_past_dates / len(submap_points_gdf)
                submap_color = custom_cmap(PATH, ratio)

                points_coords = np.array([
                    (point.x, point.y) for point in submap_points_gdf.geometry
                ])

                # Path to submap shapefiles
                shapefile_dir = PATH + '/submaps/'

                # Load submap
                submap_gdf = gpd.read_file(shapefile_dir + submap + ".shp")

                # Plot submap
                submap_gdf.plot(ax=plt.gca(), edgecolor="black", linewidth=1, color=submap_color, alpha=1)
            
            # Plot All Points for Scaling
            points_gdf.plot(
                ax=plt.gca(), 
                color=color_unvisited, 
                linewidth=0, 
                markersize=marker_size*(SCALE*SCALE), 
                alpha=1
            )
            
            # Plot Visited Points
            visited = points_gdf['date'] < current_date # mask for visited points
            if visited.any():
                points_gdf[visited].plot(
                    ax=plt.gca(), 
                    color=color_visited, 
                    linewidth=0, 
                    markersize=marker_size*(SCALE*SCALE), 
                    alpha=1
                )

            # Plot Active Points
            active = points_gdf['date'] == current_date # mask for active points
            if active.any():
                points_gdf[active].plot(
                    ax=plt.gca(), 
                    color=color_active, 
                    linewidth=0, 
                    markersize=marker_size*(SCALE*SCALE), 
                    alpha=1
                )

            # Plot All Points for Scaling
            points_gdf.plot(
                ax=plt.gca(), 
                color="black", 
                linewidth=0, 
                markersize=marker_size*(SCALE*SCALE), 
                alpha=0
            )

            # Plot Location Names
            if SCALE >= 3:
                row, column = 0, 0
                for index, location in df.iterrows():

                    if location['date'] == current_date:
                        label_color = color_active
                    elif location['date'] < current_date:
                        label_color = color_visited
                    else:
                        label_color = color_unvisited
                    pos_x = labels["Start Longitude"] + labels["Horizontal Spacing"]*column
                    pos_y = labels["Start Latitude"] - labels["Vertical Spacing"]*row

                    # Plot the label text
                    plt.text(pos_x, pos_y, location['name'], fontsize=labels["Font"]*SCALE, color=label_color)

                    row += 1
                    if row % labels["Splits"] == 0:
                        column += 1
                        row = 0
                
            # Add Plot Data and Save
            plt.title(title, fontsize=25*SCALE, color='#EAEAEA')
            plt.xlim([-12, 52])
            plt.ylim([34, 72])
            plt.axis("off")
            plt.savefig(f"./plots/temp/{PATH}_{current_date.strftime("%y%m%d")}.png")

            # Resize Plot
            with Image.open(f'./plots/temp/{PATH}_{current_date.strftime("%y%m%d")}.png') as image: # load the image
                width, height = image.size # pull image size
                if SCALE < 3:
                    x1, y1, x2, y2 = crop_s
                else:
                    x1, y1, x2, y2 = crop_l
                crop_box = (width*x1, height*y1, width*x2, height*y2)
                cropped_image = image.crop(crop_box) # crop image
                cropped_image.save(f'./plots/temp/{PATH}_{current_date.strftime("%y%m%d")}.png') # save
                # print("Figure cropped.")

                # Save the last plot in the general file
                cropped_image.save(f'./plots/{PATH}_{SCALE}.png') # save

            plt.close(fig)

    # Update Current Date into Old Date 
    old_date = current_date

# Create gif from produced plots
make_gif.create_gif(input_folder='./plots/temp', output_gif=f"./gifs/{PATH}_{SCALE}.gif", duration=200)

# Clean temp directory
temp_path = "plots/temp/"
for f in os.listdir(temp_path):
    print(f)
    os.remove(os.path.join(temp_path, f))