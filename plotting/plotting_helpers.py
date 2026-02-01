def plot_location_labels(ax, locations_df, current_date, labels_config, scale, color_unvisited, color_visited, color_active):    

    # Sort Locations
    locations_df_sorted = locations_df.sort_values("latitude", ascending=False).reset_index(drop=True)

    adjusted_df = spread_longitudes(
        locations_df_sorted,
        lon_threshold=labels_config["Longitude Threshold"],
        lat_threshold=labels_config["Latitude Threshold"],
        shift_step=labels_config["Shift Step"]
    )

    for _, location in adjusted_df.iterrows():

        date = location['date']
        lon = location["longitude"]
        lat = location["latitude"]

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
            va="center"
        )

def spread_longitudes(locations_df_sorted, lon_threshold, lat_threshold, shift_step):

    for pos, (i, loc) in enumerate(locations_df_sorted.iterrows()):

        lat = loc["latitude"]
        lon = loc["longitude"]

        if i > 0:

            previous_rows = locations_df_sorted.loc[:pos-1]

            for _, prev_loc in previous_rows.iterrows():

                prev_lat = prev_loc["latitude"]
                prev_lon = prev_loc["longitude"]
                
                if abs(lat - prev_lat) < lat_threshold and abs(lon - prev_lon) < lon_threshold:
                    
                    lat = prev_lat - shift_step
            
            locations_df_sorted.at[i, "latitude"] = lat

    return locations_df_sorted