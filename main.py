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


WEIGHTS = {
    "NP": 1.0,
    "NPres": 0.7,
    "NM": 0.5,
    "NHP": 0.5,
    "NMP":0.5,
    "NB": 0.5,
    "NL": 0.5,
    "NS": 0.5
}


def plot_voronoi(counter, index, geodf, basemap, projection, site):
    # Setup the Voronoi axes; this creates the Voronoi regions
    ax = geoplot.voronoi(
        geodf, # Define the GeoPandas DataFrame
        figsize=(20,14), # Define resolution of figure
        hue='values', # df column used to color regions
        clip=basemap,  # Define the voronoi clipping (map edge) -TODO VA source here?
        projection=projection, # Define the Projection
        cmap='YlGn', # color set
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
    
    # Format date
    date_list = list(map(str, str(site['date'])))
    year_list, month_list, day_list = date_list[:4], date_list[4:6], date_list[6:] 
    year = map(str, year_list)
    year = ''.join(year)
    month = map(str, month_list)
    month = ''.join(month)
    day = map(str, day_list)
    day = ''.join(day)
    # year = ''.join(date_list[:4])
    plt.title(f'{site['name']} {site['designation']}, {month}/{day}/{year}', fontsize=36, loc='right')
    plt.savefig(f'plots/nps_segments_{counter}.png')
    plt.close()

# CSV into DataFrame
df = pd.read_table("nps_list.csv", delimiter =",")

# Sort the dataframe by date
df = df.sort_values(by=['date'])

# Import USA data for region clipping
USA = geopandas.read_file(geoplot.datasets.get_path('contiguous_usa'))

# Set the map projection
proj = geoplot.crs.AlbersEqualArea(central_longitude=-98, central_latitude=39.5)

# Iterate through sites visited
counter = 0
for index, row in df.iterrows():
    # if not np.isnan(row['date']):
    if row['date'] != 0:
        # Set current region to active
        df.at[index,'values'] = 1

        # Convert df to gdf (GeoPandas DataFrame)
        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        # df['geometry'] = geometry
        gdf = geopandas.GeoDataFrame(df, geometry=geometry)

        # Plot the current map state
        counter += 1
        # plot_voronoi(counter, index, geodf=gdf, basemap=USA, projection=proj, site=row)
        # print(row)
        # Set current region to inactive
        df.at[index,'values'] = 0.75

print(counter)
plot_voronoi(counter, index, geodf=gdf, basemap=USA, projection=proj, site=row)