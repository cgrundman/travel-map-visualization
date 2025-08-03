from matplotlib.colors import LinearSegmentedColormap


class CustomCmap:
    """
    A class that creates a custom linear colormap from two hex color values and 
    returns interpolated colors for a given ratio between 0 and 1.

    Attributes:
    ----------
    color_1 : tuple
        The first color as an RGB tuple (converted from hex).
    color_2 : tuple
        The second color as an RGB tuple (converted from hex).
    cmap : LinearSegmentedColormap
        The matplotlib colormap object created from the two colors.

    Methods:
    -------
    value(ratio: float) -> tuple:
        Returns the interpolated RGBA color for a given ratio between 0 and 1.
    """

    def __init__(self, color_1, color_2):
        """
        Initialize the CustomCmap with two hex color strings.

        Parameters:
        ----------
        color_1 : str
            The starting color in hex format (e.g. '#3288bd').
        color_2 : str
            The ending color in hex format (e.g. '#d53e4f').
        """
        self.color_1 = hex_to_rgb(color_1)
        self.color_2 = hex_to_rgb(color_2)

        # Convert RGB tuples to normalized floats for matplotlib (0–1 range)
        self.cmap = LinearSegmentedColormap.from_list(
            "custom_map", 
            [tuple([x / 255 for x in (self.color_1)]), 
             tuple([x / 255 for x in (self.color_2)])])


    def value(self, ratio):
        """
        Get the RGBA color corresponding to the input ratio.

        Parameters:
        ----------
        ratio : float
            A float between 0 and 1 representing the interpolation level.

        Returns:
        -------
        tuple
            An RGBA color tuple (each value between 0 and 1).
        """
        # Clamp the ratio between 0 and 1
        ratio = max(0.0, min(1.0, ratio))
        return self.cmap(ratio)


def hex_to_rgb(hex_code):
    """
    Convert a hex color code to an RGB tuple.

    Parameters:
    ----------
    hex_code : str
        A hex color string (e.g. '#3288bd').

    Returns:
    -------
    tuple
        An (R, G, B) tuple with values from 0 to 255.
    """
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))