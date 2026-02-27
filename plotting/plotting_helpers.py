#from shapely.geometry import Point
from shapely.affinity import translate


def plot_location_labels(ax, locations_df, current_date, labels_config, scale, color_unvisited, color_visited, color_active):    

    # Sort Locations
    locations_df_sorted = locations_df.sort_values("latitude", ascending=False).reset_index(drop=True)

    adjusted_df = adjust_overlapping_points(
        locations_df_sorted,
        lon_thresh=labels_config["Longitude Threshold"],
        lat_thresh=labels_config["Latitude Threshold"],
        shift_step=labels_config["Shift Step"]
    )

    for _, location in adjusted_df.iterrows():

        date = location['date']
        lon = location["geometry"].x
        lat = location["geometry"].y

        if date == current_date:
            label_color = color_active
        elif date < current_date:
            label_color = color_visited
        else:
            label_color = color_unvisited

        ax.text(
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