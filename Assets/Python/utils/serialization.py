import struct
import numpy as np


def p_list(data: list) -> bytes:
    ret = struct.pack("!i", len(data))
    for item in data:
        ret += pack(item)
    return ret


def pack(data) -> bytes:
    if data is None:
        return b'\x00'
    elif isinstance(data, int):
        return b'\x01' + struct.pack("!i", data)
    elif isinstance(data, float):
        return b'\x02' + struct.pack("!f", data)
    elif isinstance(data, list):
        return b"\x03" + p_list(data)

    # Auto convert other data types
    elif isinstance(data, np.ndarray):
        return pack(data.tolist())

    else:
        raise NotImplementedError(f"Failed to pack object of type: {type(data)}")


def u_list(data: list):
    ret = []
    size, data = struct.unpack("!i", data[:4])[0], data[4:]
    for _ in range(size):
        item, data = unpack(data)
        ret.append(item)
    return ret, data


def unpack(data: bytes):
    try:
        identifier, data = data[:1], data[1:]
        if identifier == b"\x00":
            return None, data
        elif identifier == b"\x01":
            return struct.unpack("!i", data[:4])[0], data[4:]
        elif identifier == b"\x02":
            return struct.unpack("!f", data[:4])[0], data[4:]
        elif identifier == b"\x03":
            return u_list(data)
        else:
            raise NotImplementedError(f"Failed to unpack identifier with ID: {identifier}")
    except Exception as e:
        print(f"IDENTIFIER: {identifier}")
        print(f"REMAINING DATA: {data}")
        raise e
