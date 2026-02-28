#from shapely.geometry import Point
from adjustText import adjust_text
import numpy as np
from scipy.spatial.distance import pdist, squareform
import pandas as pd

def plot_location_labels(ax, locations_df, current_date, labels_config, scale, color_unvisited, color_visited, color_active):    

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
            zorder=1
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
                facecolor="#545454",
                #alpha=0.8,
                edgecolor="none"
            )
        )

        texts.append(txt)
    

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