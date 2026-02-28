#from shapely.geometry import Point
from shapely.affinity import translate
from adjustText import adjust_text
import numpy as np
from scipy.spatial.distance import pdist, squareform

def plot_location_labels(ax, locations_df, current_date, labels_config, scale, color_unvisited, color_visited, color_active):    

    # Sort Locations
    #locations_df_sorted = locations_df.sort_values("latitude", ascending=False).reset_index(drop=True)
    locations_df_sorted = (locations_df.sort_values("latitude", ascending=False).reset_index(drop=True))
    #adjusted_df = adjust_overlapping_points(
    #    locations_df_sorted,
    #    lon_thresh=labels_config["Longitude Threshold"],
    #    lat_thresh=labels_config["Latitude Threshold"],
    #    shift_step=labels_config["Shift Step"]
    #)

    texts = []

    for _, location in locations_df_sorted.iterrows():

        date = location['date']
        lon = location["geometry"].x
        lat = location["geometry"].y

        if date == current_date:
            label_color = color_active
        elif date < current_date:
            label_color = color_visited
        else:
            label_color = color_unvisited

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

    coords = np.array([(t.get_position()) for t in texts])
    dist_matrix = squareform(pdist(coords))

    threshold = 0.1  # depends on your CRS
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

    for text, (_, row) in zip(texts, locations_df.iterrows()):
        new_lon, new_lat = text.get_position()

        adjusted_positions.append({
            "name": row["name"],
            "label_longitude": new_lon,
            "label_latitude": new_lat
        })

    locations_df_sorted.to_csv("locations_with_labels.csv", index=False)

#def spread_longitudes(loc_df, lon_threshold, lat_threshold, shift_step):
#    for pos, (i, loc) in enumerate(loc_df.iloc[1:].iterrows()):
#        lat = loc["geometry"].y
#        lon = loc["geometry"].x
#        previous_rows = loc_df.loc[:pos-1]
#        for _, prev_loc in previous_rows.iterrows():
#            prev_lat = prev_loc["geometry"].y
#            prev_lon = prev_loc["geometry"].x
#            if abs(lat - prev_lat) < lat_threshold or abs(lon - prev_lon) < lon_threshold:
#                new_lat = prev_lat - shift_step
#                old_point = loc_df.at[i, "geometry"]
#                new_point = Point(old_point.x, new_lat)
#                loc_df.at[i, "geometry"] = new_point
#                if prev_loc["submap"] == "DC":
#                    print(prev_loc["submap"])
#                    print(prev_loc["geometry"].y, prev_loc["geometry"].x)
#                    print(new_point)
#    return loc_df

def adjust_overlapping_points(gdf, lat_thresh, lon_thresh, shift_step=0.01):

    accepted_points = []

    for i in range(len(gdf)):
        point = gdf.iloc[i].geometry
        lat = point.y
        lon = point.x

        needs_shift = False

        for prev_point in accepted_points:
            prev_lat = prev_point.y
            prev_lon = prev_point.x

            if abs(lat - prev_lat) < lat_thresh and \
               abs(lon - prev_lon) < lon_thresh:
                needs_shift = True
                
                break

        if needs_shift:
            # shift slightly (you can change logic here)
            new_point = translate(point, yoff=shift_step)

            print(gdf.iloc[i].submap)
            print(gdf.iloc[i].geometry)
            
        else:
            new_point = point

        # Update geometry in original dataframe
        gdf.iloc[i, gdf.columns.get_loc("geometry")] = new_point

        print(gdf.iloc[i].geometry)

        accepted_points.append(new_point)

    return gdf