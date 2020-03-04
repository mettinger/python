from multiprocessing import Process, Queue
import numpy as np
import time

def f(q):
    while True:
        q.get(True)
        q.put(np.random.randint(0,10, size=(2,5)), True)


if __name__ == '__main__':
    q = Queue()
    q.put(np.random.randint(0,10, size=(2,5)))
    p = Process(target=f, args=(q,))
    p.start()
    while True:
        result = q.get(True)
        q.put(result, True)
        print(" ")
        print(result) 