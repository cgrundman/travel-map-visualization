import json
import os


class MetaLoader:
    def __init__(self, path: str):
        """
        Initializes the MetaLoader with the base path to the project directory.
        
        :param path: Directory containing the meta_data.json file.
        """
        self.meta_path = os.path.join(path, "meta_data.json")

    def load(self) -> dict:
        """
        Loads and returns the metadata from the meta_data.json file.

        :return: A dictionary with all metadata fields.
        :raises FileNotFoundError: If the file does not exist.
        :raises json.JSONDecodeError: If the file is not valid JSON.
        """
        with open(self.meta_path, 'r') as f:
            meta_data = json.load(f)

        return meta_data