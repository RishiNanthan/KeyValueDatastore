from pathlib import Path
import json
from .datahandler.FileHandler import DataStoreFileHandler


class LargeDataStore:

    def __init__(self, filename: Path):
        self.file = filename
        self.data_handler = DataStoreFileHandler(filename)

    def create_key_value(self, key: str, value: dict, time_to_live: int = None) -> bool:
        if not (isinstance(key, str) or len(key) <= 32):
            raise Exception("Key must be 32 character of Type str")
        if not isinstance(value, dict):
            raise Exception("Value must be of Type dict")
        if time_to_live is not None and not isinstance(time_to_live, int):
            raise Exception("Time to live must be integer value denoting number of seconds")

        if self.file.stat().st_size >= 1024 * 1024 * 1024:
            raise Exception("File size reached 1GB")

        if len(json.dumps(value)) > 16 * 1024:
            raise Exception("Value can only have maximum size of 16KB")

        return self.data_handler.write_key_value(key, value, time_to_live)

    def read_value(self, key: str):
        if not (isinstance(key, str) or len(key) <= 32):
            raise Exception("Key must be 32 character of Type str")
        return self.data_handler.read_value(key)

    def delete_key(self, key: str):
        if not (isinstance(key, str) or len(key) <= 32):
            raise Exception("Key must be 32 character of Type str")
        return self.data_handler.delete_key(key)
