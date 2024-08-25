# Import pandas, numpy, and matplotlib
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
# Import Geopandas modules
import geopandas
import geoplot
# Import shapely to convert string lat-longs to Point objects
from shapely.geometry import Point
# Import date and time formatters
from time import strptime
import datetime


def plot_voronoi(i, geodf, basemap, projection):
    # Setup the Voronoi axes; this creates the Voronoi regions
    ax = geoplot.voronoi(
        geodf, # Define the GeoPandas DataFrame
        figsize=(20,14), # Define resolution of figure
        hue='values', # df column used to color regions
        clip=basemap,  # Define the voronoi clipping (map edge) -TODO VA source here?
        projection=projection, # Define the Projection
        cmap='Greys', # color set
        # k=None, # No. of discretized buckets to create
        legend=False, # Dont create a legend
        edgecolor='#000000', # Color of the voronoi boundaries
        linewidth=0.5 # width of the voronoi boundary lines
        )

    # Render the plot with a base map
    geoplot.polyplot(basemap,  # Base Map
                    ax=ax,  # Axis attribute we created above
                    extent=[-120, 25, -73, 49], # extent=USA.total_bounds,  # Set plotting boundaries to base map boundaries
                    edgecolor='black',  # Color of base map's edges
                    linewidth=3,  # Width of base map's edge lines
                    zorder=1  # Plot base map edges above the voronoi regions
                    )

    plt.savefig(f'plots/nps_segments_{i}.png')

# CSV into DataFrame
# df = pd.read_table("trial.csv", delimiter =",")
# df = pd.read_table("nps.csv", delimiter =",")
df = pd.read_table("nps_list.csv", delimiter =",")

# Sort the dataframe by date
# df = df.sort_values(by=['date'])

# Import USA data for region clipping
USA = geopandas.read_file(geoplot.datasets.get_path('contiguous_usa'))

# Set the map projection
proj = geoplot.crs.AlbersEqualArea(central_longitude=-98, central_latitude=39.5)

# Iterate through sites visited
counter = 0
for index, row in df.iterrows():
    # if not np.isnan(row['date']):
    if row['date'] != 0:
        print(row['date'], type(row['date']))
        # Set current region to active
        df.at[index,'values'] = 1

        # Convert df to gdf (GeoPandas DataFrame)
        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        # df['geometry'] = geometry
        gdf = geopandas.GeoDataFrame(df, geometry=geometry)

        # Plot the current map state
        counter += 1
        plot_voronoi(counter, geodf=gdf, basemap=USA, projection=proj)

        # Set current region to inactive
        df.at[index,'values'] = 0.75

counter += 1
plot_voronoi(counter, geodf=gdf, basemap=USA, projection=proj)