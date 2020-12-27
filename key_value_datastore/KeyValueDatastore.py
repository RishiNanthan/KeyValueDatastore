import subprocess
import requests
import json
from pathlib import Path

URL = "http://localhost:5000"

class KeyValueDataStore:

    def __init__(self, filename=None):
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
            print(self.filename)
        else:
            raise Exception(data["error"])


    def create(self, key: str, value: dict, time_to_live: int=None):
        if len(key) > 32:
            raise Exception("Key size must be less than or equal to 32 characters")
        
        data = json.dumps(value)
        req = requests.get(f"{ URL }/write?client_id={ self.__client_id }&key={ key }&value={ data }&time_to_live={ time_to_live }")
        data = req.json()

        if not data["success"]:
            raise Exception(data["error"])
        return True

    
    def read(self, key: str) -> dict:
        if len(key) > 32:
            raise Exception("Key size must be less than or equal to 32 characters")

        req = requests.get(f"{ URL }/read?client_id={ self.__client_id }&key={ key }")
        data = req.json()

        if not data["success"]:
            raise Exception(data["error"])

        return data["value"]


    def delete(self, key: str):
        if len(key) > 32:
            raise Exception("Key size must be less than or equal to 32 characters")

        req = requests.get(f"{ URL }/delete?client_id={ self.__client_id }&key={ key }")
        data = req.json()

        if not data["success"]:
            raise Exception(data["error"])

        return True

    def close(self):
        req = requests.get(f"{ URL }/close?client_id={ self.__client_id }")

