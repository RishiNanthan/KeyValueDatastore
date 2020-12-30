import json
import base64

filename = "sample.txt"


def encode(string: str) -> bytes:
    return base64.b64encode(string.encode("utf-8"))


def decode(encoded: bytes):
    return base64.b64decode(encoded)


#  Used to store int so that changes don't affect the entire file 

def get_8digit_hex(n: int):
    s = hex(n)[2:]
    if len(s) < 8:
        s = (8 - len(s)) * "0" + s
    return s


class FileHandler:

    def __init__(self, filepath):
        self.filepath = filepath

    @staticmethod
    def create_pointer(start: int, end: int):
        pointer = {
            'start': get_8digit_hex(start),
            'end': get_8digit_hex(end)
        }

        return pointer

    def read_start_pointer(self):
        fp = open(self.filepath, "r")
        line = fp.readline().strip()
        fp.close()

        start = json.loads(line)
        return start

    def create_data_file(self):
        with open(self.filepath, "x") as f:
            f.close()

        fp = open(self.filepath, "rb+")

        start_pointer = self.create_pointer(0, 0)
        start_pointer = json.dumps(start_pointer)
        start_pointer = start_pointer.encode("utf-8")

        fp.write(start_pointer)
        fp.write("\n".encode("utf-8"))
        fp.close()

    def get_keys(self):
        # Start Pointer is available in the first line of the file

        fp = open(self.filepath, "r")
        start = fp.readline().strip()
        fp.close()
        start = json.loads(start)

        if start["start"] == start["end"] == get_8digit_hex(0):  # NULL POINTER
            return None

        # GET the key from using start and end value in the start pointer
        else:
            keys = []
            next_pointer = start
            fp = open(self.filepath, "rb")

            while not next_pointer["start"] == next_pointer["end"] == get_8digit_hex(0):
                key_start = int(next_pointer["start"], 16)
                key_end = int(next_pointer["end"], 16)
                offset = key_end - key_start
                fp.seek(key_start)
                key = fp.read(offset)
                key = key.decode("utf-8")
                key = json.loads(key)
                keys.append(key)
                next_pointer = key["next_key"]

            fp.close()
            return keys

    def write_key_value(self, Key: str, Value: dict):
        keys = self.get_keys()
        value = json.dumps(Value)
        value = encode(value)

        # Empty File
        if keys is None:
            fp = open(self.filepath, "ab")
            value_start = fp.tell()

            fp.write(value)
            value_end = fp.tell()

            value_pointer = self.create_pointer(value_start, value_end)

            key = {
                'key': Key,
                'value': value_pointer,
                'next_key': self.create_pointer(0, 0),
            }

            key = json.dumps(key)
            key = key.encode("utf-8")

            key_start = value_end
            fp.write(key)
            key_end = fp.tell()
            fp.close()

            start_pointer = self.create_pointer(key_start, key_end)
            start_pointer = json.dumps(start_pointer)
            start_pointer = start_pointer.encode("utf-8")

            fp = open(self.filepath, "r+b")
            fp.write(start_pointer)
            fp.close()

        else:
            for key in keys:
                if key["key"] == Key:
                    raise Exception("Key Already Exists.")

            fp = open(self.filepath, "ab")
            value_start = fp.tell()
            fp.write(value)
            value_end = fp.tell()

            key = {
                "key": Key,
                "value": self.create_pointer(value_start, value_end),
                "next_key": self.create_pointer(0, 0),
            }

            key = json.dumps(key)
            key = key.encode("utf-8")

            key_start = value_end
            fp.write(key)
            key_end = fp.tell()
            fp.close()

            # If only one key is present, to find the key address we need to get start
            if len(keys) == 1:
                fp = open(self.filepath, "r")
                line = fp.readline().strip()
                fp.close()

                start_pointer = json.loads(line)
                prev_key_start = int(start_pointer["start"], 16)

                fp = open(self.filepath, "r+b")
                fp.seek(prev_key_start)

                prev_key = keys[-1]
                prev_key["next_key"] = self.create_pointer(key_start, key_end)
                prev_key = json.dumps(prev_key)
                prev_key = prev_key.encode("utf-8")

                fp.write(prev_key)
                fp.close()

            else:
                prev_key = keys[-1]
                prev_key["next_key"] = self.create_pointer(key_start, key_end)
                prev_key = json.dumps(prev_key)
                prev_key = prev_key.encode("utf-8")

                prev_key_start = int(keys[-2]["next_key"]["start"], 16)

                fp = open(self.filepath, "r+b")
                fp.seek(prev_key_start)
                fp.write(prev_key)
                fp.close()

    def read_value(self, Key: str):
        keys = self.get_keys()
        for key in keys:
            if key["key"] == Key:
                value_start = int(key["value"]["start"], 16)
                value_end = int(key["value"]["end"], 16)

                fp = open(self.filepath, "rb")
                fp.seek(value_start)
                value = fp.read(value_end - value_start)
                fp.close()

                value = decode(value).decode("utf-8")
                value = json.loads(value)

                return value

        raise Exception("Key not found")

    def delete_key(self, Key: str):
        keys = self.get_keys()

        if keys is None:
            raise Exception("No Key is Found")

        for i, key in enumerate(keys):
            if key["key"] == Key:
                # First key to be deleted, make start to point second if exists, else NULL
                if i == 0:
                    start_pointer = key["next_key"]
                    start_pointer = json.dumps(start_pointer)
                    start_pointer = start_pointer.encode("utf-8")

                    fp = open(self.filepath, "r+b")
                    fp.write(start_pointer)
                    fp.write("\n".encode("utf-8"))
                    fp.close()

                else:
                    prev_pointer = keys[i - 1]
                    prev_pointer["next_key"] = key["next_key"]
                    prev_pointer = json.dumps(prev_pointer)
                    prev_pointer = prev_pointer.encode("utf-8")

                    if i - 1 == 0:
                        start_pointer = self.read_start_pointer()
                        prev_pointer_start = int(start_pointer["start"], 16)

                        fp = open(self.filepath, "r+b")
                        fp.seek(prev_pointer_start)
                        fp.write(prev_pointer)
                        fp.close()

                    else:
                        prev_pointer_start = int(keys[i - 2]["next_key"]["start"], 16)

                        fp = open(self.filepath, "r+b")
                        fp.seek(prev_pointer_start)
                        fp.write(prev_pointer)
                        fp.close()

                return True

        raise Exception("No such Key Found")


file_handler = FileHandler("sample.txt")
# file_handler.create_data_file()
print(file_handler.get_keys())
# print(file_handler.write_key_value("hello2", {"a": 2, "msg": "He;llo World"}))
# print(file_handler.read_value("hello"))
# print(file_handler.delete_key("hello1"))
# print(file_handler.read_value("hello"))
