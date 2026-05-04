import pandas as pd
import datetime

from metadata.meta_loader import MetaLoader
from data.points_loader import PointsLoader
from data.bgmaps_loader import BGmapsLoader
from plotting.plotting_manager import PlotManager
from plotting.gif_generator import GifGenerator
from utils.file_utils import ensure_directory_exists

# Map Directory
# US NP | Germany | Europe | Iran |
#  "us" |    "de" |   "eu" | "ir" |
PATH = "eu"

small_map = False
small_gif = False
large_map = True

# Ensure output folders exist
ensure_directory_exists("plots/temp")
ensure_directory_exists("plots")
ensure_directory_exists("gifs")

# Load the JSON Meta-Data, Points data, and map data
meta_data = MetaLoader(PATH).load()
points_gdf = PointsLoader(PATH).load()
submaps = meta_data["Submaps"]
expansions = meta_data["Expansions"]
bgmaps = BGmapsLoader(PATH).load()

# Create a sorted values df
points_sorted = points_gdf.sort_values('date')

# Generate plots
old_date = None
plot_manager = PlotManager(
    points_gdf=points_gdf,
    submaps=submaps,
    expansions=expansions,
    bgmaps=bgmaps,
    meta_data=meta_data,
    path=PATH,
    scale=1
)

# Create gif from produced plots
gif = GifGenerator(
    input_folder="./plots/temp",
    output_gif=f"./gifs/{PATH}_{1}.gif",
    duration=200
)

current_date = points_sorted['date'].min() - datetime.timedelta(days=1)

if small_gif:
    # Add first plot
    plot_manager.generate_plot(current_date, points_sorted.iloc[0], copy=True)

# Plot all dates
for _, row in points_sorted.iterrows():
    current_date = row['date']
    if pd.notna(current_date) and current_date != old_date:
        if small_gif:
            plot_manager.generate_plot(current_date, row)
        old_date = current_date

# Create Last Plot
old_date += datetime.timedelta(days=1)

if small_gif:
    plot_manager.generate_plot(old_date, row, copy=True)

    # Generate GIF
    gif.create_gif()

elif small_map:
    plot_manager.generate_plot(old_date, row, copy=False)


# Large Plot
if large_map:
    plot_manager = PlotManager(
        points_gdf=points_gdf,
        submaps=submaps,
        expansions=expansions,
        bgmaps=bgmaps,
        meta_data=meta_data,
        path=PATH,
        scale=5
    )

    plot_manager.generate_plot(old_date, row, copy=False)

# File Cleanup
gif.cleanup_temp()
