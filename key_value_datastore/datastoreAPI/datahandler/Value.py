import json
from .utils import encode, decode


class Value:
    
    def __init__(self, value: dict, time_to_live: int = None):
        self.value = value
        self.time_to_live = time_to_live
        self.value_string = json.dumps({
            "value": value,
            "time_to_live": time_to_live,
        })


    def get_json(self):
        return {
            "value": self.value,
            "time_to_live": self.time_to_live,
        }


    def get_bytes(self):
        return encode(self.value_string)


    def __str__(self):
        return self.value_string


def Value_from_encoded_string(encoded_str: str) -> Value:
    value = decode(encoded)
    value = json.loads(value)    
    return Value(value["value"], value["time_to_live"])


def Value_from_encoded_bytes(encoded_bytes: bytes) -> Value:
    encoded = encoded_bytes.decode("utf-8")
    return value_from_encoded_string(encoded)
