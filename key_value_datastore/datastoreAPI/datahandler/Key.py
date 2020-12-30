import json
from .Pointer import Pointer


class Key:

    def __init__(self, key: str, value_pointer: Pointer, next_key: Pointer = None):
        self.key = key
        self.value_pointer = value_pointer
        self.next_key = next_key if next_key is not None else Pointer(0, 0)

    def get_json(self):
        return {
            "key": self.key,
            "value_pointer": self.value_pointer.get_json(),
            "next_key": self.next_key.get_json(),
        }

    def get_bytes(self):
        return self.__str__().encode("utf-8")

    def __str__(self):
        return json.dumps(self.get_json())


def key_from_string(key_str: str) -> Key:
    key = json.loads(key_str)
    value_pointer = Pointer(int(key["value_pointer"]["start"], 16), int(key["value_pointer"]["end"], 16))
    next_key = Pointer(int(key["next_key"]["start"], 16), int(key["next_key"]["end"], 16))
    return Key(key["key"], value_pointer, next_key)


def key_from_bytes(key_bytes: bytes) -> Key:
    key = key_bytes.decode("utf-8")
    return key_from_string(key)
