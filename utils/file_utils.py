import os
from PIL import Image


def ensure_directory_exists(directory: str):
    """Create the directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def list_files_with_extension(directory: str, extension: str):
    """List all files in a directory with a given extension."""
    return [f for f in os.listdir(directory) if f.endswith(extension)]


def cleanup_directory(directory: str, verbose: bool = False):
    """Delete all files in the given directory."""
    if not os.path.exists(directory):
        return
    for f in os.listdir(directory):
        file_path = os.path.join(directory, f)
        if os.path.isfile(file_path):
            if verbose:
                print(f"Deleting: {file_path}")
            os.remove(file_path)


def crop_and_save_image(input_path: str, output_path: str, crop_box: tuple = (.5,.5,1,1)):
    """
    Crop an image and save it.

    Args:
        input_path (str): Path to the image to crop.
        output_path (str): Path to save the cropped image.
        crop_box (tuple): A tuple (x1, y1, x2, y2) representing crop box in pixel coordinates.
    """
    with Image.open(input_path) as img:
        cropped = img.crop(crop_box)
        cropped.save(output_path)


def get_image_dimensions(image_path: str):
    """Return (width, height) of the image."""
    with Image.open(image_path) as img:
        return img.size