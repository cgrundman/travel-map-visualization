import os
import matplotlib.pyplot as plt
import geopandas as gpd

from utils.file_utils import (
    crop_and_save_image,
    get_image_dimensions,
)
from plotting.plotting_helpers import plot_location_labels


from colormap.cmap_maker import CustomCmap


class PlotManager:
    def __init__(self, points_gdf, submaps, meta_data, path, scale):
        self.points_gdf = points_gdf
        self.submaps = submaps
        self.meta_data = meta_data
        self.path = path
        self.scale = scale

        # Extract metadata fields for plotting
        self.title = meta_data["Title"]
        self.fig_size = meta_data["Figure Size"]
        self.crop_s = meta_data["Cropping"]["small"]
        self.crop_l = meta_data["Cropping"]["large"]
        self.xlims = meta_data["Plotting Area"]["xlims"]
        self.ylims = meta_data["Plotting Area"]["ylims"]
        self.color_unvisited = meta_data["Colors"]["unvisited"]
        self.color_active = meta_data["Colors"]["active"]
        self.color_visited = meta_data["Colors"]["visited"]
        self.marker_size = meta_data["Marker Size"]
        self.labels = meta_data["Labels"]
        self.map_dark = meta_data["Colors"]["map_dark"]
        self.map_light = meta_data["Colors"]["map_light"]

        self.output_temp_path = "./plots/temp/"
        self.output_final_path = "./plots/"

    def generate_plot(self, current_date, row, copy=False):
        self.copy = copy
        print(f"{current_date.date()} - {row['name']}")
        fig, ax = self._initialize_plot()
        self._plot_submaps(ax, current_date)
        self._plot_points(ax, current_date)
        self._plot_labels(ax, current_date)
        self._finalize_and_save_plot(fig, current_date)

    def _initialize_plot(self):
        fig, ax = plt.subplots(figsize=(
            self.fig_size[0] * self.scale,
            self.fig_size[1] * self.scale
        ))
        fig.patch.set_facecolor('#3C4048')
        return fig, ax

    def _plot_submaps(self, ax, current_date):
        for submap in self.submaps:
            submap_points = self.points_gdf[self.points_gdf['submap'] == submap]
            num_past_dates = (submap_points['date'] <= current_date).sum()
            ratio = num_past_dates / len(submap_points)
            color = CustomCmap(self.map_dark, self.map_light).value(ratio)

            shapefile_path = os.path.join(self.path, "submaps", f"{submap}.shp")
            submap_gdf = gpd.read_file(shapefile_path)
            submap_gdf.plot(ax=ax, edgecolor="black", linewidth=1, color=color, alpha=1)

    def _plot_points(self, ax, current_date):
        scale_factor = self.marker_size * (self.scale ** 2)

        # Unvisited
        self.points_gdf.plot(ax=ax, color=self.color_unvisited, linewidth=0, markersize=scale_factor, alpha=1)

        # Visited
        visited = self.points_gdf['date'] < current_date
        if visited.any():
            self.points_gdf[visited].plot(ax=ax, color=self.color_visited, linewidth=0, markersize=scale_factor, alpha=1)

        # Active
        active = self.points_gdf['date'] == current_date
        if active.any():
            self.points_gdf[active].plot(ax=ax, color=self.color_active, linewidth=0, markersize=scale_factor, alpha=1)

        # Invisible layer to force map scaling
        self.points_gdf.plot(ax=ax, color="black", linewidth=0, markersize=scale_factor, alpha=0)

    def _plot_labels(self, ax, current_date):
        if self.scale >= 3:
            plot_location_labels(
                ax,
                self.points_gdf,
                current_date,
                self.labels,
                self.scale,
                self.color_unvisited,
                self.color_visited,
                self.color_active
            )

    def _finalize_and_save_plot(self, fig, current_date):
        plt.title(self.title, fontsize=25 * self.scale, color='#EAEAEA')
        plt.xlim(self.xlims)
        plt.ylim(self.ylims)
        plt.axis("off")

        if self.copy:
            for i in range(5):
                filename = f"{self.path}_{current_date.strftime('%y%m%d')}_{i+1}.png"
                full_temp_path = os.path.join(self.output_temp_path, filename)
                full_final_path = os.path.join(self.output_final_path, f"{self.path}_{self.scale}.png")
                plt.savefig(full_temp_path)
                self.trim_image(full_temp_path, full_final_path)
        else:
            filename = f"{self.path}_{current_date.strftime('%y%m%d')}.png"
            full_temp_path = os.path.join(self.output_temp_path, filename)
            full_final_path = os.path.join(self.output_final_path, f"{self.path}_{self.scale}.png")
            plt.savefig(full_temp_path)
            self.trim_image(full_temp_path, full_final_path)
        plt.close(fig)

    def trim_image(self, full_temp_path, full_final_path):

        width, height = get_image_dimensions(full_temp_path)
        crop = self.crop_s if self.scale < 3 else self.crop_l
        crop_box = (width*crop[0], height*crop[1], width*crop[2], height*crop[3])

        # Crop for temp and final path
        crop_and_save_image(full_temp_path, full_final_path, crop_box)
        crop_and_save_image(full_temp_path, full_temp_path, crop_box)