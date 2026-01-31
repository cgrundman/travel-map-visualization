def plot_location_labels(ax, locations_df, current_date, labels_config, scale, color_unvisited, color_visited, color_active):    
    #LAT_THRESHOLD = 0.1   # how close in latitude counts as "same row"
    #MIN_LON_GAP  = 1.0    # minimum longitude separation
    #SHIFT_STEP   = 0.3    # how much to move when overlap found

    # Sort Locations
    locations_df_sorted = locations_df.sort_values("latitude", ascending=False)

    adjusted_df = spread_latitudes(
        locations_df_sorted,
        lon_threshold=0.15,
        min_lat_gap=0.25,
        shift_step=0.7
    )

    for _, location in adjusted_df:

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

def spread_latitudes(locations_df, lon_threshold, min_lat_gap, shift_step):
    adjusted_positions = []

    # Sort so we process nearby longitudes together
    sorted_df = locations_df.sort_values(by="longitude")

    for _, loc in sorted_df.iterrows():
        lat = loc["latitude"]
        lon = loc["longitude"]

        new_lat = lat

        # Compare with already placed points
        for prev_lon, prev_lat in adjusted_positions:

            # Only care about points in same longitude band
            if abs(lon - prev_lon) < lon_threshold:

                # If too close vertically → shift upward
                while abs(new_lat - prev_lat) < min_lat_gap:
                    new_lat += shift_step

        adjusted_positions.append((lon, new_lat))

    return adjusted_positions