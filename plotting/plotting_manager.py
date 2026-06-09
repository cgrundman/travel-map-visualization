import os
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import random
#import matplotlib.patches as patches
import matplotlib.image as mpimg
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import geopandas as gpd
from shapely import affinity
from shapely.geometry import Polygon
from scipy.spatial.distance import pdist, squareform
from adjustText import adjust_text

from utils.file_utils import (
    crop_and_save_image,
    get_image_dimensions,
)

#from plotting.plotting_helpers import plot_location_labels
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

        self.output_temp_path = "./plots/temp/"
        self.output_final_path = "./plots/"

    def generate_plot(self, current_date, row, copy=False):
        self.copy = copy
        print(f"{current_date.date()} - {row['name']}")
        fig, ax = self._initialize_plot()
        self.points_working = self.points_gdf.copy(deep=True)
        self._plot_background(ax, zorder=20)
        self._plot_submaps(ax, current_date, zorder=30)
        self._plot_expansions(ax, current_date, self.points_working)
        self._plot_text(ax, self.text, zorder=40)
        if self.plot_scale >= 3:
            self.plot_location_labels(ax, self.points_working, current_date, self.labels, self.plot_scale, self.colors["unvisited"], self.colors["visited"], self.colors["active"], self.colors["label_bg"], zorder=50)
        else:
            self._plot_points(ax, current_date, points=self.points_working, zorder=50)
        self._plot_points(ax, current_date, points=self.points_working, zorder=50, a_type="clear")
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
                ha="left",
                va="top",
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
                bgmap_gdf.plot(ax=ax, facecolor="none", edgecolor=(self.colors["bg_land_border"], alpha), linewidth=lw/self.plot_scale, zorder=zorder+1)

            # Water Borders
            for lw, alpha in self.borders["Water"]:
                bgmap_gdf.plot(ax=ax, facecolor="none", edgecolor=(self.colors["bg_water_border"], alpha), linewidth=lw/self.plot_scale, zorder=3)


    def _plot_submaps(self, ax, current_date, zorder):

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
        
        self.ratios = {}
        
        # Submap Plotting
        for submap in self.submaps:

            # Plot Backing to Shifted Submaps
            if submap["Shift"][0] != 0 or submap["Shift"][1] != 0:
            # If list is [[lon, lat], ...]
                coords = [(p[0], p[1]) for p in submap["BG"]]

                if submap["C"] == "bg_land":
                    color = self.colors["bg_land"]
                else:
                    color = self.colors["bg_water"]

                polygon = Polygon(coords)

                gdf = gpd.GeoDataFrame(geometry=[polygon])

                gdf.plot(
                    ax=ax,
                    color=color,
                    alpha=0.8,
                    edgecolor="black",
                    linewidth=4,
                    zorder=zorder
                )

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
            color = CustomCmap(self.colors["map_dark"], submap["Color"]).value(ratio)

            submap_gdf.plot(
                ax=ax,
                facecolor=color,
                edgecolor="none",
                zorder=zorder
            )

            # Scale and Shift Map
            submap_gdf["geometry"] = submap_gdf["geometry"].apply(
                lambda geom: affinity.scale(geom, xfact=scale[0], yfact=scale[1], origin=(0, 0)),
            )
            submap_gdf["geometry"] = submap_gdf["geometry"].apply(
                lambda geom: affinity.translate(geom, xoff=xoff, yoff=yoff)
            )

            # Scale and Shift Points
            mask = self.points_working['submap'] == submap["Name"]

            submap_points = self.points_working.loc[mask].copy()

            submap_points["geometry"] = submap_points["geometry"].apply(
                lambda geom: affinity.scale(
                    geom,
                    xfact=scale[0],
                    yfact=scale[1],
                    origin=(0, 0)
                )
            )

            submap_points["geometry"] = submap_points["geometry"].apply(
                lambda geom: affinity.translate(
                    geom,
                    xoff=xoff,
                    yoff=yoff
                )
            )

            # Write transformed geometries back into working copy
            self.points_working.loc[mask, "geometry"] = submap_points["geometry"]

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

            # Crisp final border
            #submap_gdf.plot(
            #    ax=ax,
            #    facecolor="none",
            #    edgecolor=self.colors["map_border"],
            #    linewidth=1.2,
            #    zorder=zorder+1
            #)

            # Water Borders
            for lw, alpha in self.borders["Water"]:
                submap_gdf.plot(ax=ax, facecolor="none", edgecolor=(self.colors["bg_water_border"], alpha), linewidth=lw/self.plot_scale, zorder=1)

    def _plot_expansions(self, ax, current_date, gdf):
        # Create inset
        ax_inset = inset_axes(
        #inset_axes(
            ax,
            width="22%",
            height="22%",
            bbox_to_anchor=(0.77, 0.23, 1, 1),
            bbox_transform=ax.transAxes,
            loc="lower left"
        )

        submaps = ["BB", "BE"]

        for submap in submaps:

            shapefile_path = os.path.join(self.path, f"submaps/{submap}.shp")
            submap_gdf = gpd.read_file(shapefile_path)

            # Plot same data
            submap_gdf.plot(
                ax=ax_inset,
                color="#6F4A4A",
                linewidth=0,
                edgecolor="black",
                zorder=70)
        
            for lw, alpha in self.borders["Submap"]:
                submap_gdf.plot(
                    ax=ax_inset,
                    facecolor="none",
                    edgecolor=(self.colors["map_border"], alpha),
                    linewidth=lw,
                    zorder=71
                )

        frame = FancyBboxPatch(
            (0, 0),
            1,
            1,
            transform=ax_inset.transAxes,
            boxstyle="round,pad=0.2",
            linewidth=4,
            edgecolor="black",#self.colors["map_border"],
            facecolor=self.colors["bg_water"],
            zorder=60
        )

        # bounds: xmin, xmax, ymin, ymax
        xmin, xmax = 13.05, 13.8
        ymin, ymax = 52.32, 52.7

        gdf_subset = gdf.cx[xmin:xmax, ymin:ymax].copy()

        self._plot_points(ax_inset, current_date, gdf_subset, 80)

        ax_inset.add_patch(frame)

        # Zoom to Berlin
        ax_inset.set_xlim(xmin, xmax)
        ax_inset.set_ylim(ymin, ymax)

        # Remove ticks
        ax_inset.set_xticks([])
        ax_inset.set_yticks([])

    def _plot_points(self, ax, current_date, points, zorder, a_type="normal"):

        # Invisible layer to force map scaling
        if a_type=="clear":
            points["geometry"].plot(ax=ax, color="black", linewidth=0, markersize=self.labels["Marker Size"], alpha=0)

        else:
            # Unvisited
            unvisited = (points['date'] > current_date) | (points['date'].isna())
            if unvisited.any():
                points[unvisited].plot(ax=ax, color=self.colors["unvisited"], linewidth=1, edgecolors=self.colors["active"], markersize=self.labels["Marker Size"], alpha=1, zorder=zorder)

            # Visited
            visited = points['date'] < current_date
            if visited.any():
                points[visited].plot(ax=ax, color=self.colors["visited"], linewidth=1, edgecolors=self.colors["active"], markersize=self.labels["Marker Size"], alpha=1, zorder=zorder)

            # Active
            active = points['date'] == current_date
            if active.any():
                points[active].plot(ax=ax, color=self.colors["active"], linewidth=1, edgecolors=self.colors["active"], markersize=self.labels["Marker Size"], alpha=1, zorder=zorder)

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

    def plot_location_labels(ax, locations_df, current_date, labels_config, scale, color_unvisited, color_visited, color_active, label_bg, zorder):    

        # Sort Locations
        locations_df_sorted = (locations_df.sort_values("latitude", ascending=False).reset_index(drop=True))

        texts = []

        for _, location in locations_df_sorted.iterrows():

            date = location['date']
            lon = location["label_longitude"]
            lat = location["label_latitude"]
            point_lon = location["geometry"].x
            point_lat = location["geometry"].y

            if date == current_date:
                label_color = color_active
            elif date < current_date:
                label_color = color_visited
            else:
                label_color = color_unvisited

            ax.plot(
                [point_lon, lon],
                [point_lat, lat],
                linewidth=0.5,
                color="gray",
                zorder=zorder
            )

            txt = ax.text(
                lon,
                lat,
                location["name"],
                fontsize=labels_config["Font"] * scale,
                color=label_color,
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round,pad=0.1",
                    facecolor=label_bg,
                    #alpha=0.8,
                    edgecolor="none"
                ),
                zorder=6
            )

            texts.append(txt)

        #compute_adjusted_label_positions(ax=ax, texts=texts, loc_df=locations_df_sorted)
        

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

