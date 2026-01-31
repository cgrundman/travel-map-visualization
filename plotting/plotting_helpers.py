def plot_location_labels(ax, locations_df, current_date, labels_config, scale, color_unvisited, color_visited, color_active):    

    # Sort Locations
    locations_df_sorted = locations_df.sort_values("latitude", ascending=False).reset_index(drop=True)

    adjusted_df = spread_longitudes(
        locations_df_sorted,
        lon_threshold=1.0,
        lat_threshold=0.08,
        shift_step=0.07
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

        print(pos, "    ",loc["name"], "   ", loc["latitude"])
        lat = loc["latitude"]
        lon = loc["longitude"]

        print(lat)

        if i > 0:

            previous_rows = locations_df_sorted.loc[:pos-1]

            for j, prev_loc in previous_rows.iterrows():

                prev_lat = prev_loc["latitude"]
                prev_lon = prev_loc["longitude"]
                
                if abs(lat - prev_lat) < lat_threshold and abs(lon - prev_lon) < lon_threshold:
                    
                    #print(pos, "    ",loc["name"], "   ", lat)
                    #locations_df_sorted.loc[i, "latitude"] = prev_lat - shift_step
                    lat = prev_lat - shift_step
                    
                    #print(pos, "    ",loc["name"], "   ", lat)

            print(lat)
            locations_df_sorted.at[i, "latitude"] = lat
            print(locations_df_sorted.at[i, "latitude"])# = lat
            #locations_df_sorted.iloc[pos, locations_df_sorted.columns.get_loc("latitude")] = lat



    return locations_df_sorted