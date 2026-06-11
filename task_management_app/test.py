import threading
import time


def add_two_numbers(a, b):
    return a + b


def worker():
    total = add_two_numbers(5, 6)
    time.sleep(2)
    print(total)


t1 = threading.Thread(target=worker)
t1.start()

print("Hello World")
