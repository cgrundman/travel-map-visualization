import pandas as pd
import datetime

from metadata.meta_loader import MetaLoader
from data.points_loader import PointsLoader
from data.submaps_loader import SubmapsLoader
from plotting.plotting_manager import PlotManager
from plotting.gif_generator import GifGenerator
from utils.file_utils import ensure_directory_exists


# Set global variables, directories for map creation and site locations
SCALE = 5

# US National Park Global Variables
PATH = "us"

# Germany Global Variables
#PATH = "de"

# Europe Global Variables
#PATH = "eu"

# Iran Global Variables
#PATH = "ir"

# Ensure output folders exist
ensure_directory_exists("plots/temp")
ensure_directory_exists("plots")
ensure_directory_exists("gifs")

# Load the JSON Meta-Data, Points data, and map data
meta_data = MetaLoader(PATH).load()
points_gdf = PointsLoader(PATH).load()
submaps = SubmapsLoader(PATH).load()

# Create a sorted values df
points_sorted = points_gdf.sort_values('date')

# Generate plots
old_date = None
plot_manager = PlotManager(
    points_gdf=points_gdf,
    submaps=submaps,
    meta_data=meta_data,
    path=PATH,
    scale=SCALE
)

# Add first plot
current_date = points_sorted['date'].min() - datetime.timedelta(days=1)
#plot_manager.generate_plot(current_date, points_sorted.iloc[0], copy=True)

# Plot all dates
for _, row in points_sorted.iterrows():
    current_date = row['date']
    if pd.notna(current_date) and current_date != old_date:
        #plot_manager.generate_plot(current_date, row)
        old_date = current_date

# Create Last Plot
old_date += datetime.timedelta(days=1)
plot_manager.generate_plot(old_date, row, copy=False)

# Create gif from produced plots
if SCALE < 3:
    gif = GifGenerator(
        input_folder="./plots/temp",
        output_gif=f"./gifs/{PATH}_{SCALE}.gif",
        duration=200
    )
    gif.generate()
gif.cleanup_temp()
