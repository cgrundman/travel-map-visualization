# Import pandas and matplotlib
import pandas as pd
from matplotlib import pyplot as plt
# Import Geopandas modules
import geopandas
import geoplot
# Import shapely to convert string lat-longs to Point objects
from shapely.geometry import Point

# Setup Geopandas Dataframe
df = pd.DataFrame(columns = ["name", "values", "longitude", "latitude"])
df.at[0, "name"], df.at[0, "values"], df.at[0, "latitude"], df.at[0, "longitude"] = "Yellowstone NP", .9, 44.61521585844979, -110.56183829896669
df.at[1, "name"], df.at[1, "values"], df.at[1, "latitude"], df.at[1, "longitude"] = "Congaree NP", .1, 33.799103145940514, -80.74876465928375
df.at[2, "name"], df.at[2, "values"], df.at[2, "latitude"], df.at[2, "longitude"] = "Big Bend NP", .5, 29.253063567543737, -103.24975431611537
df.at[3, "name"], df.at[3, "values"], df.at[3, "latitude"], df.at[3, "longitude"] = "Olympic NP", .7, 47.901013777029945, -123.569530853349337
df.at[4, "name"], df.at[4, "values"], df.at[4, "latitude"], df.at[4, "longitude"] = "Acadia NP", .8, 44.35051799918331, -68.2744980108673
df.at[5, "name"], df.at[5, "values"], df.at[5, "latitude"], df.at[5, "longitude"] = "Everglades NP", .2, 25.393677671904296, -80.94223818892222
df.at[6, "name"], df.at[6, "values"], df.at[6, "latitude"], df.at[6, "longitude"] = "Hot Springs NP", .3, 35.48466729904587, -92.95956272911957
df.at[7, "name"], df.at[7, "values"], df.at[7, "latitude"], df.at[7, "longitude"] = "Great Smoky Mountains NP", .6, 35.88769422966946, -83.48432666049747

print(df.head())

# Assumes data stored in pandas DataFrame df
geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
print(geometry)
gdf = geopandas.GeoDataFrame(df, geometry=geometry)

# Import USA data for region clipping
USA = geopandas.read_file(geoplot.datasets.get_path('contiguous_usa'))

# Set the map projection
proj = geoplot.crs.AlbersEqualArea(central_longitude=-98, central_latitude=39.5)

# Setup the Voronoi axes; this creates the Voronoi regions
ax = geoplot.voronoi(gdf,  # Define the GeoPandas DataFrame
                     hue='values',  # df column used to color regions
                     clip=USA,  # Define the voronoi clipping (map edge)
                     projection=proj,  # Define the Projection
                     cmap='RdBu',  # color set
                    #  k=None,  # No. of discretized buckets to create
                     legend=True, # Create a legend
                     edgecolor='#ffffff',  # Color of the voronoi boundaries
                     linewidth=0.5  # width of the voronoi boundary lines
                    )
# Render the plot with a base map
geoplot.polyplot(USA,  # Base Map
                 ax=ax,  # Axis attribute we created above
                 extent=USA.total_bounds,  # Set plotting boundaries to base map boundaries
                 edgecolor='black',  # Color of base map's edges
                 linewidth=1,  # Width of base map's edge lines
                 zorder=1  # Plot base map edges above the voronoi regions
                 )

plt.savefig('foo.png')