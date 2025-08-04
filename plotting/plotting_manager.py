import os
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

from utils.file_utils import (
    crop_and_save_image,
    get_image_dimensions,
)

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

        self.output_temp_path = "./plots/temp/"
        self.output_final_path = "./plots/"

    def generate_all_plots(self):
        old_date = None
        for _, row in self.points_gdf.iterrows():
            current_date = row['date']
            if pd.notna(current_date) and current_date != old_date:
                print(f"{current_date.date()} - {row['name']}")
                fig, ax = self._initialize_plot()
                self._plot_submaps(ax, current_date)
                self._plot_points(ax, current_date)
                self._plot_labels(ax, current_date)
                self._finalize_and_save_plot(fig, current_date)
                old_date = current_date

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
            color = CustomCmap(self.path, ratio)

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
        if self.scale < 3:
            return

        row = column = 0
        for _, location in self.points_gdf.iterrows():
            date = location['date']
            if date == current_date:
                label_color = self.color_active
            elif date < current_date:
                label_color = self.color_visited
            else:
                label_color = self.color_unvisited

            pos_x = self.labels["Start Longitude"] + self.labels["Horizontal Spacing"] * column
            pos_y = self.labels["Start Latitude"] - self.labels["Vertical Spacing"] * row
            ax.text(pos_x, pos_y, location['name'], fontsize=self.labels["Font"] * self.scale, color=label_color)

            row += 1
            if row % self.labels["Splits"] == 0:
                column += 1
                row = 0

    def _finalize_and_save_plot(self, fig, current_date):
        filename = f"{self.path}_{current_date.strftime('%y%m%d')}.png"
        full_temp_path = os.path.join(self.output_temp_path, filename)
        full_final_path = os.path.join(self.output_final_path, f"{self.path}_{self.scale}.png")

        plt.title(self.title, fontsize=25 * self.scale, color='#EAEAEA')
        plt.xlim(self.xlims)
        plt.ylim(self.ylims)
        plt.axis("off")
        plt.savefig(full_temp_path)
        plt.close(fig)

        width, height = get_image_dimensions(full_temp_path)
        crop = self.crop_s if self.scale < 3 else self.crop_l
        crop_box = (width * crop[0], height * crop[1], width * crop[2], height * crop[3])

        # Crop for temp and final path
        crop_and_save_image(full_temp_path, full_temp_path, crop_box)
        crop_and_save_image(full_temp_path, full_final_path, crop_box)