import json
from .utils import get_hex


class Pointer:

    def __init__(self, start: int, end: int):
        self.start = get_hex(start)
        self.end = get_hex(end)
        self.start_val = start
        self.end_val = end


    def isNullPointer(self):
        return self.start_val == self.end_val == 0


    def get_json(self):
        return {
            "start": self.start,
            "end": self.end,
        }


    def get_bytes(self):
        return self.__str__().encode("utf-8")


    def __str__(self):
        return json.dumps(self.get_json())


def Pointer_from_string(pointer: str) -> Pointer:
    pointer = json.loads(pointer)
    start = int(pointer["start"], 16)
    end = int(pointer["end"], 16)

    return Pointer(start, end)

def Pointer_from_bytes(pointer: bytes) -> Pointer:
    pointer = pointer.decode("utf-8")
    return Pointer_from_string(pointer)

