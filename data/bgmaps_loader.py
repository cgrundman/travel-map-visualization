import os

class BGmapsLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        """
        Loads and returns a sorted list of submap names (without '.shp') from the submaps directory.
        """
        bgmaps_dir = f"{self.path}/bg_maps"
        submap_files = os.listdir(bgmaps_dir)

        bgmaps = [
            filename.replace('.shp', '')
            for filename in submap_files
            if filename.endswith('.shp')
        ]
        bgmaps.sort()
        return bgmaps