import re
import struct
from datetime import datetime


def count_pattern(text: str, pattern: str = r"\{.*?\}"):
    return len(re.findall(pattern, text))


def datatime2unix(date_string: str, datatime_format: str = '%Y-%m-%d %H:%M:%S.%f') -> float:
    date_obj = datetime.strptime(date_string, datatime_format)
    timestamp = date_obj.timestamp()
    return timestamp


def float2binary64(value: float):
    packed = struct.pack('d', value)
    return packed


def int2binary64(value: int):
    binary_data = struct.pack('q', value)
    return binary_data


def str_datatime2binary64(value: str):
    return float2binary64(datatime2unix(value))

