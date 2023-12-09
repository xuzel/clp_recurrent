import re
import struct
from datetime import datetime


def count_pattern(text: str, pattern: str = r"\{.*?\}") -> int:
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


def binary64_to_float(binary_data: str) -> float:
    return struct.unpack('d', binary_data)[0]


def float2datatime(value: float) -> str:
    dt_object = datetime.fromtimestamp(value)
    formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S.%f')
    return formatted_date


def binary64_to_datatime(binary_data) -> str:
    return float2datatime(binary64_to_float(binary_data))


def binary64_to_int(binary_data: bytes) -> int:
    return struct.unpack('q', binary_data)[0]


def replace_first_bracket(text: str, replacement: str, pattern: str = r'\{.*?\}'):
    return re.sub(pattern, replacement, text, count=1)