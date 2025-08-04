import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

class PointsLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        """
        Loads and returns a cleaned GeoDataFrame with a datetime 'date' column and a Point geometry column.
        """
        csv_path = f"{self.path}/locations.csv"
        df = pd.read_csv(csv_path)

        # Parse 'date' column; replace invalid (e.g., 0) with NaT
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d', errors='coerce')

        # Sort by date for consistency in plotting
        df_sorted = df.sort_values('date')

        # Create geometry column
        geometry = [Point(xy) for xy in df_sorted[['longitude', 'latitude']].values]
        gdf = gpd.GeoDataFrame(df_sorted, geometry=geometry)

        # Set CRS to WGS84 (EPSG:4326)
        gdf.set_crs(epsg=4326, inplace=True)

        return gdf
