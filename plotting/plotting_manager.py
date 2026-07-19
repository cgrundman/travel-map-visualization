import os
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import random
#import matplotlib.patches as patches
import matplotlib.image as mpimg
import matplotlib.patches as patches
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle
#from matplotlib.patches import FancyBboxPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import geopandas as gpd
#from shapely import affinity
#from shapely.geometry import Polygon, box
#from shapely.geometry import box
from scipy.spatial.distance import pdist, squareform
from adjustText import adjust_text

from utils.file_utils import (
    crop_and_save_image,
    get_image_dimensions,
)

#from plotting.plotting_helpers import _plot_labels
from colormap.cmap_maker import CustomCmap

random.seed(5)

#1. background
#2. background_maps
#3. main_maps / submaps
#4. borders
#5. expansions / insets
#6. grid
#7. points
#8. state_labels
#9. text_annotations
#10. flags / legend / title

class PlotManager:
    def __init__(self, points_gdf, submaps, expansions, bgmaps, meta_data, path, scale):
        self.points_gdf = points_gdf
        self.submaps = submaps
        self.expansions = expansions
        self.bgmaps = bgmaps
        self.meta_data = meta_data
        self.path = path
        self.plot_scale = scale

        # Extract metadata fields for plotting
        self.text = meta_data["Text"]
        self.plotting = meta_data["Plotting"]
        self.colors = meta_data["Colors"]
        self.labels = meta_data["Labels"]
        self.borders = meta_data["Borders"]
        self.expansion_props = meta_data["Expanion Properties"]

        self.output_temp_path = "./plots/temp/"
        self.output_final_path = "./plots/"

    def generate_plot(self, current_date, row, copy=False):
        self.copy = copy
        print(f"{current_date.date()} - {row['name']}")
        fig, ax = self._initialize_plot()

        #Establish point df's
        self.points_working = self.points_gdf.copy(deep=True)
        self._find_ratios(current_date)
        points_main = self._exclude_expansion_points(self.points_working)
        self._plot_background(ax, zorder=20)
        self._plot_submaps(ax, self.submaps, zorder=30)

        # Inset still gets original/full points
        self._plot_expansions(ax, current_date, self.points_working, zorder=40)
        self._plot_text(ax, self.text, zorder=50)

        if self.plot_scale >= 3:
            self._plot_labels(
                ax,
                points_main,
                current_date,
                self.labels,
                self.plot_scale,
                self.colors["unvisited"],
                self.colors["visited"],
                self.colors["active"],
                self.colors["label_bg"],
                zorder=60
            )
        else:
            self._plot_points(ax, current_date, points=points_main, zorder=60)

        self._plot_points(ax, current_date, points=points_main, zorder=60, a_type="clear")
        self._plot_flags(ax)
        self._finalize_and_save_plot(fig, ax, current_date)

    def _initialize_plot(self):
        fig, ax = plt.subplots(
            figsize=(
                self.plotting["Figure Size"][0],
                self.plotting["Figure Size"][1],
            ), 
            dpi=100*self.plot_scale
        )
        fig.patch.set_facecolor(self.colors["bg"])
        return fig, ax
    
    def _plot_text(self, ax, text, zorder):

        for text in self.text:

            ax.text(
                text["x"],                     # x position in axes coords
                text["y"],                     # y position in axes coords
                text["text"],
                transform=ax.transAxes,
                fontsize=text["size"],
                fontfamily=text["font"],
                fontweight=text["weight"],
                color=text["color"],
                ha="center",
                va="center",
                zorder=zorder,
                alpha=1
            )

    def _plot_background(self, ax, zorder):
        # Background Map Plotting
        for bgmap in self.bgmaps:

            shapefile_path = os.path.join(self.path, "bg_maps", f"{bgmap}.shp")
            bgmap_gdf = gpd.read_file(shapefile_path)

            # Base fill
            bgmap_gdf.plot(
                ax=ax,
                facecolor=self.colors["bg_land"],
                edgecolor="none",
                zorder=zorder
            )

            # BG Map Borders
            for lw, alpha in self.borders["Background Map"]:
                bgmap_gdf.plot(ax=ax, facecolor="none", edgecolor=(self.colors["bg_land_border"], alpha), linewidth=lw, zorder=zorder+1)

            # Water Borders
            for lw, alpha in self.borders["Water"]:
                bgmap_gdf.plot(ax=ax, facecolor="none", edgecolor=(self.colors["bg_water_border"], alpha), linewidth=lw, zorder=3)

    def _find_ratios(self, current_date):
        self.ratios = {}

        for submap in self.submaps:
            # Copy points gdf
            submap_points = self.points_gdf.loc[
                self.points_gdf['submap'] == submap["Name"]
            ].copy()

            # Establish time frame
            num_past_dates = (submap_points['date'] <= current_date).sum()

            # Caöculate Ratio and save to dictionary
            ratio = num_past_dates / len(submap_points)
            self.ratios[submap["Name"]] = ratio


    def _plot_submaps(self, ax, submaps, zorder):

        # Plot Region for water
        min_lon, max_lon = self.plotting["Plotting Area"]["xlims"][0], self.plotting["Plotting Area"]["xlims"][1]
        min_lat, max_lat = self.plotting["Plotting Area"]["ylims"][0], self.plotting["Plotting Area"]["ylims"][1]
        width = max_lon - min_lon
        height = max_lat - min_lat
        rect = patches.Rectangle(
            (min_lon, min_lat),   # bottom-left corner
            width,
            height,
            facecolor=self.colors["bg_water"],
            alpha=1
        )
        ax.add_patch(rect)
                
        # Submap Plotting
        for submap in submaps:

            name = submap["Name"]

            shapefile_path = os.path.join(self.path, "submaps", f"{name}.shp")
            submap_gdf = gpd.read_file(shapefile_path)

            
            #ratio = self.ratios[submap["Name"]]
            ratio = 1
            color = CustomCmap(self.colors["map_dark"], submap["Color"]).value(ratio)

            submap_gdf.plot(
                ax=ax,
                facecolor=color,
                edgecolor="none",
                zorder=zorder
            )

            # Base fill
            submap_gdf.plot(
                ax=ax,
                facecolor=color,
                edgecolor="none",
                zorder=zorder+1
            )

            # Border Map Layers
            for lw, alpha in self.borders["Submap"]:
                submap_gdf.plot(
                    ax=ax,
                    facecolor="none",
                    edgecolor=(self.colors["map_border"], alpha),
                    linewidth=lw,
                    zorder=zorder+2
                )

            # Water Borders
            for lw, alpha in self.borders["Water"]:
                submap_gdf.plot(
                    ax=ax, 
                    facecolor="none", 
                    edgecolor=(self.colors["bg_water_border"], alpha), 
                    linewidth=lw, 
                    zorder=1
                )

    def _plot_expansions(self, ax, current_date, points_gdf, zorder):

        for expansion in self.expansions:
        
            xmin, xmax, ymin, ymax = expansion["Coords"]
            bbox_to_anchor = expansion["bbox_to_anchor"]
            height, width = expansion["height/width"]

            # Create inset
            ax_inset = inset_axes(
                ax,
                width=width,
                height=height,
                bbox_to_anchor=bbox_to_anchor,
                bbox_transform=ax.transAxes,
                loc="lower left"
            )

            submaps_filtered = [
                submap.copy()
                for submap in self.submaps
                if submap["Name"] in expansion["Submaps"]
            ]

            self._plot_submaps(ax_inset, submaps_filtered, zorder)

            # Find contained points
            points_in_expansion = points_gdf.cx[xmin:xmax, ymin:ymax].copy()

            if self.plot_scale >= 3:
                self._plot_labels(ax_inset, points_in_expansion, current_date, self.labels, self.plot_scale, self.colors["unvisited"], self.colors["visited"], self.colors["active"], self.colors["label_bg"], zorder=60)
            else:
                self._plot_points(ax_inset, current_date, points=points_in_expansion, zorder=zorder+2)

            ax_inset.set_facecolor(self.colors["bg_water"])

            for spine in ax_inset.spines.values():
                spine.set_visible(False)

            # Zoom to Berlin
            ax_inset.set_xlim(xmin, xmax)
            ax_inset.set_ylim(ymin, ymax)

            frame = Rectangle(
                (0, 0),                  # Lower-left corner in axes coordinates
                1,                       # Width (100% of inset)
                1,                       # Height (100% of inset)
                transform=ax_inset.transAxes,
                facecolor="none",
                edgecolor=self.colors["map_border"],
                linewidth=self.expansion_props["Borders"]["width"],
                clip_on=False,
                zorder=zorder+3
            )

            ax_inset.add_patch(frame)

            # Remove ticks
            ax_inset.set_xticks([])
            ax_inset.set_yticks([])

            ax_inset.text(
                expansion["x"],
                expansion["y"],
                expansion["Text"],
                transform=ax_inset.transAxes,
                color=self.expansion_props["Text"].get("color", self.expansion_props["Text"]["color"]),
                fontsize=self.expansion_props["Text"].get("size", self.expansion_props["Text"]["size"]),
                fontfamily=self.expansion_props["Text"].get("font", "DejaVu Sans"),
                fontweight=self.expansion_props["Text"].get("weight", 600),
                ha=self.expansion_props["Text"].get("ha", "center"),
                va=self.expansion_props["Text"].get("va", "center"),
                zorder=zorder+2
            )

    def _plot_points(self, ax, current_date, points, zorder, a_type="normal"):

        # Invisible layer to force map scaling
        if a_type=="clear":
            points["geometry"].plot(ax=ax, color="black", linewidth=0, markersize=self.labels["Marker Size"], alpha=0)

        else:
            # Unvisited
            unvisited = (points['date'] > current_date) | (points['date'].isna())
            if unvisited.any():
                points[unvisited].plot(ax=ax, color=self.colors["unvisited"], linewidth=self.labels["Marker Border"], edgecolors=self.colors["active"], markersize=self.labels["Marker Size"], alpha=1, zorder=zorder)

            # Visited
            visited = points['date'] < current_date
            if visited.any():
                points[visited].plot(ax=ax, color=self.colors["visited"], linewidth=self.labels["Marker Border"], edgecolors=self.colors["active"], markersize=self.labels["Marker Size"], alpha=1, zorder=zorder)

            # Active
            active = points['date'] == current_date
            if active.any():
                points[active].plot(ax=ax, color=self.colors["active"], linewidth=self.labels["Marker Border"], edgecolors=self.colors["active"], markersize=self.labels["Marker Size"], alpha=1, zorder=zorder)

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
            if ratio > 1:
                frameon = True

            # Create color image
            if ratio > 0.5:
                #beta = ratio*2 - 1
                beta = 1
            else:
                beta = 0
            img = mpimg.imread(f"./{self.path}/submaps/{file}")
            rounded_mask = img[:, :, 3].copy()
            if img.shape[-1] == 3:
                img = np.dstack([img, np.ones(img.shape[:2])])
            img[:,:,3] = img[:,:,3]*beta

            # Create grayscale image
            if ratio == 0:
                alpha = 0
            else:
                #alpha = ratio*2
                alpha = 1
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
                    edgecolor=border_color,   # border color
                    linewidth=flag_linewidth, # border thickness
                    boxstyle=f"round,pad=0.3,rounding_size={flag_radius}",  
                                              # rounded corners
                    facecolor=border_color,   # background behind image
                    alpha=1.0                 # border opacity
                )
            )
            ax.add_artist(imagebox_img)

    def _finalize_and_save_plot(self, fig, ax, current_date):
        ax.set_xlim(self.plotting["Plotting Area"]["xlims"])
        ax.set_ylim(self.plotting["Plotting Area"]["ylims"])
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
            width*self.plotting["Cropping"][0], 
            height*self.plotting["Cropping"][1], 
            width*self.plotting["Cropping"][2], 
            height*self.plotting["Cropping"][3]
        )

        # Crop for temp and final path
        crop_and_save_image(full_temp_path, full_final_path, crop_box)
        crop_and_save_image(full_temp_path, full_temp_path, crop_box)

    def _plot_labels(self, ax, locations_df, current_date, labels_config, scale, color_unvisited, color_visited, color_active, label_bg, zorder):    

        # Sort Locations
        locations_df_sorted = (locations_df.sort_values("latitude", ascending=False).reset_index(drop=True))

        # Filter for locations visited
        locations_df_sorted = locations_df_sorted[locations_df_sorted["date"] <= current_date].copy()

        texts = []

        for _, location in locations_df_sorted.iterrows():

            #date = location['date']
            lon = location["label_longitude"]
            lat = location["label_latitude"]
            #point_lon = location["geometry"].x
            #point_lat = location["geometry"].y

            # Shifts Plot
            #ax.plot(
            #    [point_lon, lon],
            #    [point_lat, lat],
            #    linewidth=0.5,
            #    color="gray",
            #    zorder=zorder
            #)

            txt = ax.text(
                lon, lat, location["name"],
                fontsize=5.5,
                color='black',
                ha="center",
                va="center",
                path_effects=[pe.withStroke(linewidth=1, foreground=self.colors["bg_land"])],
                zorder=zorder
            )

            texts.append(txt)

        #compute_adjusted_label_positions(ax=ax, texts=texts, loc_df=locations_df_sorted)
        
    def _exclude_expansion_points(self, points_gdf):
        points_filtered = points_gdf.copy()
        for expansion in self.expansions:
            xmin, xmax, ymin, ymax = expansion["Coords"]
            inside_expansion = points_filtered.cx[xmin:xmax, ymin:ymax].index
            points_filtered = points_filtered.drop(index=inside_expansion)
        
        return points_filtered
    
    def compute_adjusted_label_positions(ax, texts, loc_df):
        """
        Run adjust_text and extract adjusted label positions.
        """

        coords = np.array([(t.get_position()) for t in texts])
        dist_matrix = squareform(pdist(coords))

        threshold = 0.1
        cluster_indices = np.where((dist_matrix < threshold) & (dist_matrix > 0))
        cluster_indices = np.unique(cluster_indices[0])

        clustered_texts = [texts[i] for i in cluster_indices]

        adjust_text(
            clustered_texts,
            ax=ax,
            force_text=1.0,
            force_points=0.05,
            expand_text=(0.0, 10.0),
            expand_points=(1.5, 1.5),
            arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
            lim=1000
        )

        # Extract adjusted positions
        adjusted_positions = []

        for text, (_, row) in zip(texts, loc_df.iterrows()):
            new_lon, new_lat = text.get_position()

            adjusted_positions.append({
                "name": row["name"],
                "label_longitude": new_lon,
                "label_latitude": new_lat
            })

        adjusted_loc_df = pd.DataFrame(adjusted_positions)

        loc_df["label_latitude"] = adjusted_loc_df["label_latitude"].apply(lambda x: f"{x:6.6f}")
        loc_df["label_longitude"] = adjusted_loc_df["label_longitude"].apply(lambda x: f"{x:6.6f}")

        loc_df = loc_df[['submap','latitude','longitude', 'label_latitude', 'label_longitude','date','name']]

        loc_df["date"] = pd.to_datetime(loc_df["date"], errors="coerce")
        loc_df["date"] = loc_df["date"].dt.strftime("%Y%m%d")
        loc_df["date"] = loc_df["date"].astype("Int64")  # nullable integer type
        
        loc_df.to_csv("locations_with_labels.csv", index=False, float_format="%.6f")

        return loc_df

