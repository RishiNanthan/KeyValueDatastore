import json
from pathlib import Path
import time


class CRD:

    def __init__(self, filepath: Path):
        self.path = filepath

    def read(self, key: str) -> dict:
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

    def write(self, key: str, value: str, timeToLive=None):
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

    def delete(self, key: str):
        with self.path.open("r") as fp:
            file_data = json.load(fp)

        if key in file_data.keys():
            file_data.pop(key)

            with self.path.open("w") as fp:
                json.dump(file_data, fp)
            return True

        raise Exception("No such Key")
