import os

class BOmapsLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        """
        Loads and returns a sorted list of submap names (without '.shp') from the submaps directory.
        """
        bomaps_dir = f"{self.path}/bo_maps"
        bomap_files = os.listdir(bomaps_dir)

        bomaps = [
            filename.replace('.shp', '')
            for filename in bomap_files
            if filename.endswith('.shp')
        ]
        bomaps.sort()
        return bomaps