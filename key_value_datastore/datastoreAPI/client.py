from pathlib import Path
from hashlib import sha1
from .datahandler.utils import encode
from .CRD_SmallDatastore import SmallDataStore
from .CRD_LargeDatastore import LargeDataStore


class Client:

    def __init__(self, client_id: int, filename: Path, datastore_type: str = "small"):
        self.client_id = client_id
        self.filename = filename
        self.datastore_type = datastore_type
        self.client_token = None
        self.get_token()
        self.crd = SmallDataStore(self.filename) if datastore_type == "small" else LargeDataStore(self.filename)

    def get_token(self):
        if self.client_token is not None:
            return self.client_token

        string = f"{self.client_id}: {str(self.filename)}"
        h = sha1()
        h.update(string)
        token_bytes = h.digest()
        self.client_token = encode(token_bytes).decode("utf-8")
        return self.client_token

    def read_value(self, key: str):
        return self.crd.read_value(key)

    def create_key_value(self, key: str, value: dict, time_to_live: int):
        return self.crd.create_key_value(key, value, time_to_live)

    def delete_key(self, key: str):
        return self.crd.delete_key(key)

    def __str__(self):
        return self.client_token
