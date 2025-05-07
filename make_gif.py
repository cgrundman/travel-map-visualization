import os
from PIL import Image

def create_gif(input_folder, output_gif, duration=200):
    """
    Creates an animated GIF from a folder of image files.

    Parameters:
    -----------
    input_folder : str
        Path to the folder containing image files (JPG, JPEG, PNG).
    output_gif : str
        File path (including .gif extension) for the output animated GIF.
    duration : int, optional
        Duration between frames in milliseconds. Default is 200ms.

    Raises:
    -------
    ValueError:
        If no valid image files are found in the input folder.
    """

    # List all files in the input folder and filter by valid image extensions
    image_files = sorted([
        f for f in os.listdir(input_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])

    # If no image files were found, raise an error
    if not image_files:
        raise ValueError("No image files found in the folder.")

    # Open each image and convert to RGB to ensure consistency
    images = [Image.open(os.path.join(input_folder, file)).convert('RGB') for file in image_files]

    # Get the size of the first image and resize all images to match
    width, height = images[0].size
    images = [img.resize((width, height)) for img in images]

    # Save the first image and append the rest to create the animated GIF
    images[0].save(
        output_gif,               # Output file path
        save_all=True,            # Save all frames
        append_images=images[1:], # Append the rest of the images
        duration=duration,        # Duration per frame in ms
        loop=0                    # Loop forever
    )

    print(f"GIF saved as {output_gif}")