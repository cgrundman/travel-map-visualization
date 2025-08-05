from utils.file_utils import cleanup_directory
import make_gif

import psutil
import os
from PIL import Image
import imageio.v2 as imageio



class GifGenerator:
    def __init__(self, input_folder: str, output_gif: str, duration: int = 200):
        self.input_folder = input_folder
        self.output_gif = output_gif
        self.duration = duration

    def generate(self):
        make_gif.create_gif(
            input_folder=self.input_folder,
            output_gif=self.output_gif,
            duration=self.duration
        )
        print(f"GIF saved to {self.output_gif}")

    def cleanup_temp(self, verbose: bool = False):
        cleanup_directory(self.input_folder, verbose=verbose)
        print(f"Cleaned up temporary files in {self.input_folder}")

    
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

        print("Load images.")

        # If no image files were found, raise an error
        if not image_files:
            raise ValueError("No image files found in the folder.")

        # Open each image and convert to RGB to ensure consistency
        images = [Image.open(os.path.join(input_folder, file)).convert('RGB') for file in image_files]

        print("Images loaded and created.")

        # Get the size of the first image and resize all images to match
        width, height = images[0].size
        images = [img.resize((width, height)) for img in images]

        print("Images resized.")

        # Save the first image and append the rest to create the animated GIF
        images[0].save(
            output_gif,               # Output file path
            save_all=True,            # Save all frames
            append_images=images[1:], # Append the rest of the images
            duration=duration,        # Duration per frame in ms
            loop=0                    # Loop forever
        )

        print(f"GIF saved as {output_gif}")

    def create_gif_imageio(input_folder, output_gif, duration=0.2):
        image_files = sorted([
            os.path.join(input_folder, f)
            for f in os.listdir(input_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])

        with imageio.get_writer(output_gif, mode='I', duration=duration) as writer:
            for filename in image_files:
                image = imageio.imread(filename)
                print(filename)
                print(f"Memory used: {psutil.Process(os.getpid()).memory_info().rss / 1024**2:.2f} MB")
                writer.append_data(image)

    def memory_used():
        import os
        process = psutil.Process(os.getpid())
        print(f"Memory used: {process.memory_info().rss / 1024 ** 2:.2f} MB")

    def create_gif_streamed(self, input_folder, output_gif, duration=0.2):
        image_files = sorted([
            os.path.join(input_folder, f)
            for f in os.listdir(input_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])

        with imageio.get_writer(output_gif, mode='I', duration=duration) as writer:
            for idx, filename in enumerate(image_files):
                print(f"Loading {filename}")
                image = imageio.imread(filename)  # load
                writer.append_data(image)        # write
                del image                         # force delete reference
                if idx % 10 == 0:                 # monitor memory every 10 images
                    self.memory_used()

    def get_folder_size(path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # Skip broken symlinks
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    #create_gif_streamed(
    #    input_folder='./plots/us', 
    #    output_gif='./gifs/us_5.gif'
    #)
