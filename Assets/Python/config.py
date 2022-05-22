from typing import Union
import json

import numpy as np


CONFIG_FILE = "./config.json"


def __ndarray_if_list(value):
    if type(value) == list:
        return np.array(value)
    else:
        return value


def load_config(*args, file_name=CONFIG_FILE) -> Union[tuple, dict]:
    try:
        with open(file_name, "r") as f:
            data_json = f.read()
            data: dict = json.loads(data_json)
            if len(args) > 0:
                return tuple(__ndarray_if_list(data[k]) if k in data.keys() else None for k in args)
            else:
                return data

    except Exception:
        if len(args) > 0:
            return (None for _ in args)
        else:
            return None


def save_config(file_name=CONFIG_FILE, **kwargs):
    data = load_config(file_name=file_name)
    if not data or not isinstance(data, dict):
        data = {}
    data.update(kwargs)
    data_json = json.dumps(data, indent=4)

    with open(file_name, "w") as f:
        f.write(data_json)
