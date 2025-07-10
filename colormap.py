# import matplotlib.pyplot as plt
import json
from matplotlib.colors import LinearSegmentedColormap
# import numpy as np

def custom_cmap(path, ratio):

    # Load the JSON Meta-Data
    with open(path + '/meta_data.json', 'r') as f:
        meta_data = json.load(f)
    
    # Color Ranges
    color_1 = hex_to_rgb(meta_data["Colors"]["map_dark"])
    color_2 = hex_to_rgb(meta_data["Colors"]["map_light"])

    # Create a custom linear colormap
    cmap = LinearSegmentedColormap.from_list("custom_map", [tuple([x / 255 for x in (color_1)]), tuple([x / 255 for x in (color_2)])])

    color = cmap(ratio)

    return color

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

# Function to get color at position between 0 and 1
#def get_color(value):
#    return custom_cmap(value)

# Example usage
#value = 0.25
#color_at_value = get_color(value)
#print(f"Color at {value}: {color_at_value}")

#gradient = np.linspace(0, 1, 256).reshape(1, -1)
#plt.imshow(gradient, aspect='auto', cmap=custom_cmap)
#plt.title("Custom Color Map")
#plt.axis('off')
#plt.show()