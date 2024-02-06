from slicer import Slicer
import multiprocessing as mp
from controller2 import Controller

class Wrapper:
    def __init__(self, q) -> None:
        self.queue:mp.Queue = q
        pass

    def send(self, msg):
        self.queue.put(msg)

    



if __name__ == '__main__':
    q = mp.Queue()

    w = Wrapper(q)
    s = Slicer(w.send)

    p = mp.Process(target=w., args=())

    p.start()

    s.start()
    
    

