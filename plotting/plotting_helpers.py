def plot_location_labels(ax, locations_df, current_date, labels_config, scale, color_unvisited, color_visited, color_active):
    """
    Plot labels for each location on the map based on visit status.
    """
    row = column = 0
    for _, location in locations_df.iterrows():
        date = location['date']

        if date == current_date:
            label_color = color_active
        elif date < current_date:
            label_color = color_visited
        else:
            label_color = color_unvisited

        pos_x = labels_config["Start Longitude"] + labels_config["Horizontal Spacing"] * column
        pos_y = labels_config["Start Latitude"] - labels_config["Vertical Spacing"] * row

        ax.text(
            pos_x,
            pos_y,
            location['name'],
            fontsize=labels_config["Font"] * scale,
            color=label_color
        )

        row += 1
        if row % labels_config["Splits"] == 0:
            column += 1
            row = 0
