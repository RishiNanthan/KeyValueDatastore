import json
from pathlib import Path
import time
from .CRD import CRD

class SmallDataStore(CRD):

    def __init__(self, filepath: Path):
        self.path = filepath
        self.data = {}
        if not self.path.exists():
            fp = self.path.open("x")
            fp.close()
            fp = self.path.open("w")
            fp.write("{}")
            fp.close()
        else:
            with self.path.open("r") as fp:
                self.data = json.load(fp)
                fp.close()


    def read_value(self, key: str) -> dict:
        if not isinstance(key, str) or len(key) > 32:
            raise Exception("Key must be 32 character of Type str")

        with self.path.open("r") as fp:
            json_data = json.load(fp)

        if key in json_data.keys():
            value = json_data[key]
            time_to_live = value["timeToLive"]
            if time_to_live is None or time_to_live >= time.time():
                return value["data"]
            raise Exception("Time Expired")

        raise Exception("No such Key")

    def create_key_value(self, key: str, value: str, timeToLive=None):

        if not (isinstance(key, str) or len(key) <= 32):
            raise Exception("Key must be 32 character of Type str")

        if not isinstance(value, dict):
            raise Exception("Value must be of Type dict")

        if time_to_live is not None and not isinstance(time_to_live, int):
            raise Exception("Time to live must be integer value denoting number of seconds")

        if len(json.dumps(value)) > 16 * 1024:
            raise Exception("Value can only have maximum size of 16KB")

        filesize = self.path.stat().st_size
        if filesize > 1024 * 1024 * 1024:
            raise Exception("File size is more than 1GB. Cannot write any more data.")
        data = json.loads(value)

        with self.path.open("r") as fp:
            file_data = json.load(fp)

        if key not in file_data.keys():
            file_data[key] = {
                "timeToLive": None if timeToLive is None else int(time.time()) + timeToLive,
                "data": data,
            }
            with self.path.open("w") as fp:
                json.dump(file_data, fp)

            return True

        else:
            raise Exception("Key already exists")

    def delete_key(self, key: str):
        
        if not (isinstance(key, str) or len(key) <= 32):
            raise Exception("Key must be 32 character of Type str")
        
        with self.path.open("r") as fp:
            file_data = json.load(fp)

        if key in file_data.keys():
            file_data.pop(key)

            with self.path.open("w") as fp:
                json.dump(file_data, fp)
            return True

        raise Exception("No such Key")
