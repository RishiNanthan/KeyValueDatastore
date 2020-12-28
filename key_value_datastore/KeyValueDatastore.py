import subprocess
import requests
import json
from pathlib import Path

URL = "http://localhost:5000"

class KeyValueDataStore:

    def __init__(self, filename: str=None):
        """
            Parameters:
            filename: str or None,

            Starts the datastore API if not running, If filename is None, it creates a file for storing data,
            the filename can be found by calling the method get_filename(). If filename is given, if the file is present
            initialises the datastore. 
            Throws exception on failure.
        """
        self.filename = None
        self.__client_id = None

        if filename is not None:
            assert type(filename) == "<class 'str'>"

        try:
            requests.get(URL)
        except:
            print("Running the API first")
            p = Path().cwd() / "key_value_datastore" / "datastoreAPI" / "api.py"
            subprocess.Popen(f'python "{ str(p) }"')
        
        req = None
        if filename is None:
            req = requests.get(f"{ URL }/init")
            
        else:
            req = requests.get(f"{ URL }/init?filename={ filename }")

        data = req.json()
        if data["success"]:
            self.filename = data["filename"]
            self.__client_id = data["client_id"]

        else:
            raise Exception(data["error"])


    def create(self, key: str, value: dict, time_to_live: int=None) -> bool:
        """
            Parameters:
            key: str (32 chars),
            value: dict (json value in dict format),
            time_to_live: int ( in seconds ),

            Creates a key value pair in datastore if there is no such previous key, else throws error

        """
        
        assert type(key) == type("str") and type(value) == type({"dict": 1})
        
        if time_to_live is not None:
            assert type(time_to_live) == type(1)

        if len(key) > 32:
            raise Exception("Key size must be less than or equal to 32 characters")
        
        data = json.dumps(value)
        req = requests.get(f"{ URL }/write?client_id={ self.__client_id }&key={ key }&value={ data }&time_to_live={ time_to_live }")
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

        assert type(key) == type("str")

        if len(key) > 32:
            raise Exception("Key size must be less than or equal to 32 characters")

        req = requests.get(f"{ URL }/read?client_id={ self.__client_id }&key={ key }")
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
        assert type(key) == type("str")

        if len(key) > 32:
            raise Exception("Key size must be less than or equal to 32 characters")

        req = requests.get(f"{ URL }/delete?client_id={ self.__client_id }&key={ key }")
        data = req.json()

        if not data["success"]:
            raise Exception(data["error"])

        return True


    def close(self):
        req = requests.get(f"{ URL }/close?client_id={ self.__client_id }")


    def get_filename(self):
        """
            Parameters: None

            Returns the filename

        """
        return self.filename


    def __del__(self):
        if self.__client_id is not None:
            try: 
                self.close()
            except:
                pass

