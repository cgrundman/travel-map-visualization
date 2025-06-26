import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

def custom_cmap(ratio):
    # Color Ranges
    color_1 = (132, 60, 57)
    color_2 = (214, 97, 107)

    # Create a custom linear colormap
    cmap = LinearSegmentedColormap.from_list("custom_map", [tuple([x / 255 for x in (color_1)]), tuple([x / 255 for x in (color_2)])])

    color = cmap(ratio)

    return color

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