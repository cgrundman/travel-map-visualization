import os

from metadata.meta_loader import MetaLoader
from data.points_loader import PointsLoader
from data.submaps_loader import SubmapsLoader
from plotting.plotting_manager import PlotManager
from plotting.gif_generator import GifGenerator
from utils.file_utils import ensure_directory_exists


# Set global variables, directories for map creation and site locations
SCALE = 5

# US National Park Global Variables
#PATH = "us"

# Germany Global Variables
PATH = "de"

# Europe Global Variables
#PATH = "eu"

# Ensure output folders exist
ensure_directory_exists("plots/temp")
ensure_directory_exists("plots")
ensure_directory_exists("gifs")

# Load the JSON Meta-Data, Points data, and map data
meta_data = MetaLoader(PATH).load()
points_gdf = PointsLoader(PATH).load()
submaps = SubmapsLoader(PATH).load()

# --- Generate plots ---
plot_manager = PlotManager(
    points_gdf=points_gdf,
    submaps=submaps,
    meta_data=meta_data,
    path=PATH,
    scale=SCALE
)
plot_manager.generate_all_plots()

# Create gif from produced plots
gif = GifGenerator(
    input_folder="./plots/temp",
    output_gif=f"./gifs/{PATH}_{SCALE}.gif",
    duration=200
)
gif.generate()
gif.cleanup_temp()

# Clean temp directory
temp_path = "plots/temp/"
for f in os.listdir(temp_path):
    print(f)
    os.remove(os.path.join(temp_path, f))