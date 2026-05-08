from functools import wraps
import time

def structured_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        log = {
            "function": func.__name__,
            "args": args,
            "kwargs": kwargs,
            "execution_time": round(end-start, 4)
        }
        print(log)
        return result
    return wrapper

@structured_logger
def add(a,b):
    time.sleep(1)
    return a+b

value = add(5, 10)
print("Result: ", value)