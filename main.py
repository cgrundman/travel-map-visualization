# Import pandas
import pandas as pd
# Import Geopandas modules
import geopandas
import geoplot
# Import shapely to convert string lat-longs to Point objects
from shapely.geometry import Point

# Setup Geopandas Dataframe
df = pd.DataFrame(columns = ["name", "longitude", "latitude"])
df.at[0, "name"], df.at[0, "longitude"], df.at[0, "latitude"] = "Yellowstone NP", 44.61521585844979, -110.56183829896669
df.at[1, "name"], df.at[1, "longitude"], df.at[1, "latitude"] = "Congaree NP", 33.799103145940514, -80.74876465928375
df.at[2, "name"], df.at[2, "longitude"], df.at[2, "latitude"] = "Big Bend NP", 29.253063567543737, -103.24975431611537

print(df.head())

# df.iloc[:,0]['name'], df.iloc[:,0]['longitude'], df.iloc[:,0]['latitude'] = "Yellowstone NP", 44.61521585844979, -110.56183829896669
# df.iloc[:,1]['name'], df.iloc[:,1]['longitude'], df.iloc[:,1]['latitude'] = "Congaree NP", 33.799103145940514, -80.74876465928375
# df.iloc[:,2]['name'], df.iloc[:,2]['longitude'], df.iloc[:,2]['latitude'] = "Big Bend NP", 29.253063567543737, -103.24975431611537

# # Assumes data stored in pandas DataFrame df
# geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
# gdf = geopandas.GeoDataFrame(df, geometry=geometry)

# # Import USA data for region clipping
# USA = geopandas.read_file(geoplot.datasets.get_path('contiguous_usa'))

# # Set the map projection
# proj = geoplot.crs.AlbersEqualArea(central_longitude=-98, central_latitude=39.5)

# # Setup the Voronoi axes; this creates the Voronoi regions
# ax = geoplot.voronoi(gdf,  # Define the GeoPandas DataFrame
#                      hue='values',  # df column used to color regions
#                      clip=USA,  # Define the voronoi clipping (map edge)
#                      projection=proj,  # Define the Projection
#                      cmap='Reds',  # color set
#                      k=None,  # No. of discretized buckets to create
#                      legend=True, # Create a legend
#                      edgecolor='white',  # Color of the voronoi boundaries
#                      linewidth=0.01  # width of the voronoi boundary lines
#                     )
# # Render the plot with a base map
# geoplot.polyplot(USA,  # Base Map
#                  ax=ax,  # Axis attribute we created above
#                  extent=USA.total_bounds,  # Set plotting boundaries to base map boundaries
#                  edgecolor='black',  # Color of base map's edges
#                  linewidth=1,  # Width of base map's edge lines
#                  zorder=1  # Plot base map edges above the voronoi regions
#                  )