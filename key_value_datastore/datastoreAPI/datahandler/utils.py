import base64


def encode(string: str) -> bytes:
    return base64.b64encode(string.encode("utf-8"))


def decode(encoded: bytes) -> bytes:
    return base64.b64decode(encoded)


def get_hex(n: int):
    s = hex(n)[2:]
    if len(s) < 8:
        s = (8 - len(s)) * "0" + s
    return s
