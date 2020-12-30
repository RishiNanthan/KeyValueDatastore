import subprocess
import requests
import json
from pathlib import Path

URL = "http://localhost:5000"


class KeyValueDataStore:

    def __init__(self, filename: str = None, datastore_type: str=None):
        """
            Parameters:
            filename: str or None,

            Starts the datastore API if not running, If filename is None, it creates a file for storing data,
            the filename can be found by calling the method get_filename(). If filename is given, if the file is present
            initialises the datastore. 
            Throws exception on failure.
        """
        assert isinstance(filename, str) or filename is None
        assert (isinstance(datastore_type, str) and datastore_type in ("small", "large")) or datastore_type is None

        self.filename = filename
        self.__client_token = None
        try:
            requests.get(URL)
        except:
            print("Starting the API...")
            p = Path().cwd() / "key_value_datastore" / "datastoreAPI" / "api.py"
            subprocess.Popen(f'python "{ str(p) }"')

        url = f"{ URL }/init"
        if filename is not None:
            url += f"?filename={ filename }"
        if datastore_type is not None:
            url += f"&datastore={ datastore_type }"

        req = requests.get(url)
        data = req.json()
        if data["success"]:
            self.filename = data["filename"]
            self.__client_token = data["token"]
        else:
            raise Exception(data["error"])

    def create(self, key: str, value: dict, time_to_live: int = None) -> bool:
        """
            Parameters:
            key: str (32 chars),
            value: dict (json value in dict format),
            time_to_live: int ( in seconds ),

            Creates a key value pair in datastore if there is no such previous key, else throws error

        """
        assert isinstance(key, str) and isinstance(value, dict) and (isinstance(time_to_live, int) or time_to_live is None)
        if len(key) > 32:
            raise Exception("Key size must be less than or equal to 32 characters")

        data = json.dumps(value)
        req = requests.get(
            f"{ URL }/write?token={ self.__client_token }&key={ key }&value={ data }&time_to_live={ time_to_live }")
        data = req.json()

        if not data["success"]:
            raise Exception(data["error"])
        return True

    def read(self, key: str) -> dict:
        """
            Parameters:
            key: str (32 chars),

            Gets the Value from the datastore for a given key, if key is not found throws exception
            Returns dict containing the json value

        """
        assert isinstance(key, str)
        if len(key) > 32:
            raise Exception("Key size must be less than or equal to 32 characters")

        req = requests.get(f"{ URL }/read?token={ self.__client_token }&key={ key }")
        data = req.json()

        if not data["success"]:
            raise Exception(data["error"])
        return data["value"]

    def delete(self, key: str):
        """
            Parameters:
            key: str (32 chars),

            Deletes the Key-Value pair from the datastore for a given key, if key is not found throws exception
            Returns True on success

        """
        assert isinstance(key, str)
        if len(key) > 32:
            raise Exception("Key size must be less than or equal to 32 characters")

        req = requests.get(f"{ URL }/delete?token={ self.__client_token }&key={ key }")
        data = req.json()

        if not data["success"]:
            raise Exception(data["error"])
        return True

    def close(self):
        requests.get(f"{ URL }/close?token={ self.__client_token }")

    def get_filename(self):
        """
            Parameters: None,

            Returns the filename

        """
        return self.filename

    def __del__(self):
        if self.__client_token is not None:
            try:
                self.close()
            except:
                pass
