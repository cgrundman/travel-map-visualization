import os
import numpy as np
import math
import matplotlib.pyplot as plt
import random
#import matplotlib.patches as patches
import matplotlib.image as mpimg
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import geopandas as gpd
from shapely import affinity

from utils.file_utils import (
    crop_and_save_image,
    get_image_dimensions,
)

from plotting.plotting_helpers import plot_location_labels
from colormap.cmap_maker import CustomCmap

random.seed(5)

class PlotManager:
    def __init__(self, points_gdf, submaps, bgmaps, meta_data, path, scale):
        self.points_gdf = points_gdf
        self.submaps = submaps
        self.bgmaps = bgmaps
        self.meta_data = meta_data
        self.path = path
        self.plot_scale = scale


        # Extract metadata fields for plotting
        self.title = meta_data["Title"]
        self.fig_size = meta_data["Figure Size"]
        self.crop = meta_data["Cropping"]
        self.xlims = meta_data["Plotting Area"]["xlims"]
        self.ylims = meta_data["Plotting Area"]["ylims"]
        self.color_unvisited = meta_data["Colors"]["unvisited"]
        self.color_active = meta_data["Colors"]["active"]
        self.color_visited = meta_data["Colors"]["visited"]
        self.marker_size = meta_data["Marker Size"]
        self.labels = meta_data["Labels"]
        self.map_dark = meta_data["Colors"]["map_dark"]
        self.map_light = meta_data["Colors"]["map_light"]
        self.bg_land = meta_data["Colors"]["bg_land"]
        self.bg_water = meta_data["Colors"]["bg_water"]

        self.output_temp_path = "./plots/temp/"
        self.output_final_path = "./plots/"

    def generate_plot(self, current_date, row, copy=False):
        self.copy = copy
        #print(f"{current_date.date()} - {row['name']}")
        fig, ax = self._initialize_plot()
        self._plot_submaps(ax, current_date)
        if self.plot_scale >= 3:
            self._plot_labels(ax, current_date, points=self.points_gdf)
            #self._plot_points(ax, current_date, points=self.points_gdf)
        else:
            self._plot_points(ax, current_date, points=self.points_gdf)
        self._plot_points(ax, current_date, points=self.points_gdf, type="clear")
        self._plot_flags(ax)
        self._finalize_and_save_plot(fig, current_date)

    def _initialize_plot(self):
        fig, ax = plt.subplots(
            figsize=(
                self.fig_size[0],
                self.fig_size[1],
            ), 
            dpi=100*self.plot_scale
        )
        fig.patch.set_facecolor("#FF000000")
        #fig.patch.set_facecolor('#3C4048')
        return fig, ax

    def _plot_submaps(self, ax, current_date):
        # Plot Region for water
        min_lon, max_lon = self.xlims[0], self.xlims[1]
        min_lat, max_lat = self.ylims[0], self.ylims[1]
        width = max_lon - min_lon
        height = max_lat - min_lat
        rect = patches.Rectangle(
            (min_lon, min_lat),   # bottom-left corner
            width,
            height,
            facecolor=self.bg_water,
            alpha=1
        )
        ax.add_patch(rect)
        
        self.ratios = {}

        # Background Map Plotting
        for bgmap in self.bgmaps:
            color = self.bg_land

            shapefile_path = os.path.join(self.path, "bg_maps", f"{bgmap}.shp")
            bgmap_gdf = gpd.read_file(shapefile_path)
            bgmap_gdf.plot(ax=ax, edgecolor="black", linewidth=4/self.plot_scale, color=color, alpha=1)
        
        # Submap Plotting
        for submap in self.submaps:
            #print(submap["Name"])

            map_i = submap["Name"]
            scale = submap["Scale"]
            xoff = submap["Shift"][0]
            yoff = submap["Shift"][1]

            shapefile_path = os.path.join(self.path, "submaps", f"{map_i}.shp")
            submap_gdf = gpd.read_file(shapefile_path)

            submap_points = self.points_gdf.loc[
                self.points_gdf['submap'] == submap["Name"]
            ].copy()
            num_past_dates = (submap_points['date'] <= current_date).sum()
            ratio = num_past_dates / len(submap_points)
            self.ratios[submap["Name"]] = ratio
            color = CustomCmap(self.map_dark, self.map_light).value(ratio)
                        
            # Scale and Shift Map
            submap_gdf["geometry"] = submap_gdf["geometry"].apply(
                lambda geom: affinity.scale(geom, xfact=scale[0], yfact=scale[1], origin=(0, 0)),
            )
            submap_gdf["geometry"] = submap_gdf["geometry"].apply(
                lambda geom: affinity.translate(geom, xoff=xoff, yoff=yoff)
            )

            # Scale and Shift Points
            mask = self.points_gdf['submap'] == submap["Name"]

            self.points_gdf.loc[mask, "geometry"] = (
                self.points_gdf.loc[mask, "geometry"]
                .apply(
                    lambda geom: affinity.translate(
                        geom,
                        xoff=xoff + ((scale[0] - 1) * geom.x),
                        yoff=yoff + ((scale[1] - 1) * geom.y),
                    )
                )
            )

            submap_gdf.plot(ax=ax, edgecolor="black", linewidth=1/self.plot_scale, color=color, alpha=1)

            if map_i == "VI":
                print(self.points_gdf.loc[mask, "geometry"])

            #self._plot_points(ax, current_date, points=submap_points)

    def _plot_points(self, ax, current_date, points, type="normal"):

        # Invisible layer to force map scaling
        if type=="clear":
            points.plot(ax=ax, color="black", linewidth=0, markersize=self.marker_size, alpha=0)

        else:
            # Unvisited
            points["geometry"].plot(ax=ax, color=self.color_unvisited, linewidth=0, markersize=self.marker_size, alpha=1)

            # Visited
            visited = points['date'] < current_date
            if visited.any():
                points[visited].plot(ax=ax, color='#353535', linewidth=0, markersize=self.marker_size, alpha=1)

            # Active
            active = points['date'] == current_date
            if active.any():
                points[active].plot(ax=ax, color=self.color_active, linewidth=0, markersize=self.marker_size, alpha=1)

    def _plot_labels(self, ax, current_date, points):
        plot_location_labels(
            ax,
            points,
            current_date,
            self.labels,
            self.plot_scale,
            self.color_unvisited,
            self.color_visited,
            self.color_active
        )

    def _plot_flags(self, ax):
        flag_scale = self.meta_data["Flags"]["Scale"]
        flag_radius = self.meta_data["Flags"]["Radius"]
        flag_linewidth = self.meta_data["Flags"]["Linewidth"]
        flag_positon = self.meta_data["Flags"]["Position"]
        border_color = self.meta_data["Flags"]["Linecolor"]
        
        png_files = [f for f in os.listdir(f"{self.path}/submaps") if f.lower().endswith(".png")]
        png_files.sort()
        for i, file in enumerate(png_files):
            frameon = False

            #ratio = self.ratios[file[:2]]
            ratio=1
            if ratio == 1:
                frameon = True

            # Create image
            if ratio > 0.5:
                beta = ratio*2 - 1
            else:
                beta = 0
            img = mpimg.imread(f"./{self.path}/submaps/{file}")
            rounded_mask = img[:, :, 3].copy()
            if img.shape[-1] == 3:
                img = np.dstack([img, np.ones(img.shape[:2])])
            img[:,:,3] = img[:,:,3]*beta

            # Create grayscale image
            if ratio > 0.5:
                alpha = 1
            else:
                alpha = ratio*2
            gray = np.dot(img[...,:3], [0.587, 0.299, 0.114])
            gray_rgb = np.stack((gray, gray, gray), axis=-1)

            # Copy the alpha channel from original image (rounded corners)
            alpha_channel = np.ones(gray_rgb.shape[:2]) * alpha  # preserve transparency and scale by alpha
            alpha_channel = np.multiply(alpha_channel, rounded_mask)
            
            # Combine grayscale with rounded alpha
            gray_rgba = np.dstack([gray_rgb, alpha_channel])

            row = math.floor(i / flag_positon["num_in_row"])
            column = i - flag_positon["num_in_row"]*row


            x_position = flag_positon["x_start"] + flag_positon["x_spacing"]*column
            y_position = flag_positon["y_start"] - flag_positon["y_spacing"]*row

            img_position = (x_position, y_position)

            imagebox_gry = AnnotationBbox(
                OffsetImage(gray_rgba, zoom=flag_scale), 
                img_position, 
                frameon=False, 
                xycoords='axes fraction'
            )
            ax.add_artist(imagebox_gry)

            imagebox_img = AnnotationBbox(
                OffsetImage(img, zoom=flag_scale), 
                img_position, 
                frameon=frameon, 
                xycoords='axes fraction',
                pad=0.1,                      # space between image and border
                bboxprops=dict(
                    edgecolor=border_color,    # border color
                    linewidth=flag_linewidth, # border thickness
                    boxstyle=f"round,pad=0.3,rounding_size={flag_radius}",  
                                              # rounded corners
                    facecolor=border_color,    # background behind image
                    alpha=1.0                 # border opacity
                )
            )
            ax.add_artist(imagebox_img)

    def _finalize_and_save_plot(self, fig, current_date):
        plt.xlim(self.xlims)
        plt.ylim(self.ylims)
        plt.axis("off")

        if self.copy:
            for i in range(5):
                filename = f"{self.path}_{current_date.strftime('%y%m%d')}_{i+1}.png"
                full_temp_path = os.path.join(self.output_temp_path, filename)
                full_final_path = os.path.join(self.output_final_path, f"{self.path}_{self.plot_scale}.png")
                plt.savefig(full_temp_path)
                self.trim_image(full_temp_path, full_final_path)
        else:
            filename = f"{self.path}_{current_date.strftime('%y%m%d')}.png"
            full_temp_path = os.path.join(self.output_temp_path, filename)
            full_final_path = os.path.join(self.output_final_path, f"{self.path}_{self.plot_scale}.png")
            plt.savefig(full_temp_path)
            self.trim_image(full_temp_path, full_final_path)
        plt.close(fig)

    def trim_image(self, full_temp_path, full_final_path):

        width, height = get_image_dimensions(full_temp_path)
        crop_box = (
            width*self.crop[0], 
            height*self.crop[1], 
            width*self.crop[2], 
            height*self.crop[3]
        )

        # Crop for temp and final path
        crop_and_save_image(full_temp_path, full_final_path, crop_box)
        crop_and_save_image(full_temp_path, full_temp_path, crop_box)