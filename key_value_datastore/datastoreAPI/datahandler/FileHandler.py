from pathlib import Path
import time
from .Pointer import Pointer, pointer_from_string
from .Key import Key, key_from_bytes
from .Value import Value, value_from_encoded_bytes

"""
    Since parsing a complete large json file to find a particular key-value pair takes lot of time,
    we could use keys as linked list across a file so that we could get the keys quickly first and
    then get the value by using the pointer to the value. 
"""

class DataStoreFileHandler:

    def __init__(self, filename: Path):
        self.file = filename
        self.start_pointer = None
        self.keys = None
        if not self.file.exists():
            fp = self.file.open("x")
            fp.close()

            fp = self.file.open("wb")
            start = Pointer(0, 0)
            fp.write(start.get_bytes())
            fp.write("\n".encode("utf-8"))
            fp.close()
            self.get_start()
            self.get_all_keys()
        else:
            try:
                self.get_start()
                self.get_all_keys()
            except Exception:
                raise Exception("Wrong File or Wrong Datastore type")

    # Returns the start pointer for the keys
    def get_start(self) -> Pointer:
        fp = self.file.open("r")
        start = fp.readline().strip()
        fp.close()
        self.start_pointer = pointer_from_string(start)
        return self.start_pointer

    # using the start_pointer, retrieves all the keys
    def get_all_keys(self) -> list:
        start = self.start_pointer
        keys = []
        next_pointer = start

        while not next_pointer.isNullPointer():
            key = self.read_intermediate(next_pointer.start_val, next_pointer.end_val)
            key = key_from_bytes(key)
            keys.append(key)
            next_pointer = key.next_key
        self.keys = keys
        return keys

    # checks and returns the key else raises exception
    def get_key(self, key_str: str) -> Key:
        keys = self.keys
        for key in keys:
            if key.key == key_str:
                return key
        raise Exception("No such key Found")

    # write in particular position in file without altering other data
    def write_intermediate(self, data: bytes, pos: int = 0):
        with self.file.open("r+b") as fp:
            fp.seek(pos)
            fp.write(data)
            end = fp.tell()
            fp.close()
        return end

    # read from particular position in file
    def read_intermediate(self, start: int, end: int) -> bytes:
        with self.file.open("rb") as fp:
            fp.seek(start)
            data = fp.read(end - start)
            fp.close()
        return data

    # creates a new key value pair in the datastore
    def write_key_value(self, key_str: str, value_dict: dict, time_to_live: int = None) -> bool:
        keys = self.keys
        for key in keys:
            if key.key == key_str:
                raise Exception("Key Exists.")

        # append value to the file
        fp = self.file.open("ab")
        value_start = fp.tell()
        value = Value(value_dict, time_to_live)
        fp.write(value.get_bytes())
        value_end = fp.tell()

        value_pointer = Pointer(value_start, value_end)
        key = Key(key_str, value_pointer)

        # append key to file
        key_start = value_end
        fp.write(key.get_bytes())
        key_end = fp.tell()
        fp.close()

        if len(keys) == 0:
            start = Pointer(key_start, key_end)
            self.start_pointer = start
            self.write_intermediate(start.get_bytes())

        elif len(keys) == 1:
            start = self.start_pointer
            prev_key = Key(keys[0].key, keys[0].value_pointer, Pointer(key_start, key_end))
            self.keys[-1] = prev_key
            self.write_intermediate(prev_key.get_bytes(), start.start_val)

        else:
            prev_key = Key(keys[-1].key, keys[-1].value_pointer, Pointer(key_start, key_end))
            self.keys[-1] = prev_key
            self.write_intermediate(prev_key.get_bytes(), keys[-2].next_key.start_val)

        self.keys += [key]
        return True

    # reads the value for particular key
    def read_value(self, key_str: str) -> dict:
        key = self.get_key(key_str)
        data = self.read_intermediate(key.value_pointer.start_val, key.value_pointer.end_val)
        value = value_from_encoded_bytes(data)
        if value.time_to_live is not None and value.time_to_live < time.time():
            raise Exception("Time to live Expired..")
        return value.value

    # deletes the key from the datastore keys
    def delete_key(self, key_str: str) -> bool:
        keys = self.keys.copy()

        if len(keys) == 0:
            raise Exception("No Key is Found")

        for i, key in enumerate(keys):
            if key.key == key_str:

                if i == 0:
                    start = key.next_key
                    self.start_pointer = start    # Change start to point to next->next
                    self.keys.pop(i)              # Removes deleted key from memory
                    self.write_intermediate(start.get_bytes())

                else:
                    prev_key = keys[i - 1]
                    # Object alteration changes would be reflected in self.keys[i-1] also. prev->next = cur->next
                    prev_key.next_key = key.next_key

                    if i - 1 == 0:
                        start = self.start_pointer
                        self.keys.pop(i)                # Removes deleted key from memory
                        self.write_intermediate(prev_key.get_bytes(), start.start_val)

                    else:
                        prev_key_start = keys[i - 2].next_key.start_val
                        self.keys.pop(i)                # Removes deleted key from memory
                        self.write_intermediate(prev_key.get_bytes(), prev_key_start)

                return True

        raise Exception("No such Key found")
