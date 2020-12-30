from pathlib import Path
from hashlib import sha1
from .datahandler.utils import encode, decode


class Client:

    def __init__(self, client_id: int, filename: Path, datastore_type: str = "small"):
        self.client_id = client_id
        self.filename = filename
        self.datastore_type = datastore_type
        self.client_token = None
        self.get_token()

    def get_token(self):
        if self.client_token is not None:
            return self.client_token

        string = f"{ self.client_id }: { str(self.filename) }"
        h = sha1()
        h.update(string)
        token_bytes = h.digest()
        self.client_token = encode(token_bytes).decode("utf-8")
        return self.client_token

    def __str__(self):
        return self.client_token
