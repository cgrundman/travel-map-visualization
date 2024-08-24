# Import pandas, and matplotlib
import pandas as pd
from matplotlib import pyplot as plt
# Import Geopandas modules
import geopandas
import geoplot
# Import shapely to convert string lat-longs to Point objects
from shapely.geometry import Point

def plot_voronoi(i):
    # Setup the Voronoi axes; this creates the Voronoi regions
    ax = geoplot.voronoi(
        gdf, # Define the GeoPandas DataFrame
        figsize=(20,14), # Define resolution of figure
        hue='values', # df column used to color regions
        clip=USA,  # Define the voronoi clipping (map edge) -TODO VA source here?
        projection=proj, # Define the Projection
        cmap='Greys', # color set
        # k=None, # No. of discretized buckets to create
        legend=False, # Dont create a legend
        edgecolor='#000000', # Color of the voronoi boundaries
        linewidth=0.5 # width of the voronoi boundary lines
        )

    # Render the plot with a base map
    geoplot.polyplot(USA,  # Base Map
                    ax=ax,  # Axis attribute we created above
                    extent=[-120, 25, -73, 49], # extent=USA.total_bounds,  # Set plotting boundaries to base map boundaries
                    edgecolor='black',  # Color of base map's edges
                    linewidth=3,  # Width of base map's edge lines
                    zorder=1  # Plot base map edges above the voronoi regions
                    )

    plt.savefig(f'plots/nps_segments_{i}.png')

# CSV into DataFrame
# df = pd.read_table("trial.csv", delimiter =",")
df = pd.read_table("nps.csv", delimiter =",")
# df['name'] = df['name'].astype("string") # which will by default set the length to the max len it encounters
# print(df.tail())


# gdf.set_geometry('geometry', inplace=True)

# Import USA data for region clipping
USA = geopandas.read_file(geoplot.datasets.get_path('contiguous_usa'))
# i = USA[(USA.state == 'North Carolina')].index
# USA.drop(i)

# Set the map projection
proj = geoplot.crs.AlbersEqualArea(central_longitude=-98, central_latitude=39.5)

counter = 0
for index, row in df.iterrows():
    if row['date'] != "NAN":
        df.at[index,'values'] = 1

        print(df['name'], df['values'])

        # Assumes data stored in pandas DataFrame df
        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        # print(geometry)
        df['geometry'] = geometry
        gdf = geopandas.GeoDataFrame(df, geometry=df.geometry)

        counter += 1
        plot_voronoi(counter)

        df.at[index,'values'] = 0.75

print(gdf)