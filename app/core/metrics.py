import time
from contextlib import contextmanager


@contextmanager
def timer():
    start = time.perf_counter()
    result = {"duration_ms": None}

    try:
        yield result
    finally:
        result["duration_ms"] = round(time.perf_counter()- start * 1000, 2)