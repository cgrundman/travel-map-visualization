import os

class SubmapsLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        """
        Loads and returns a sorted list of submap names (without '.shp') from the submaps directory.
        """
        submaps_dir = f"{self.path}/submaps"
        submap_files = os.listdir(submaps_dir)

        submaps = [
            filename.replace('.shp', '')
            for filename in submap_files
            if filename.endswith('.shp')
        ]
        submaps.sort()
        return submaps
