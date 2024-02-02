from slicer import Slicer
import multiprocessing as mp

class Wrapper:
    def __init__(self, q) -> None:
        self.queue:mp.Queue = q
        pass

    def send(self, msg):
        self.queue.put(msg)

    def receive(self):
        out = None
        while(not self.queue.empty()):
            out = self.queue.get()
        return out

    def receiver(self):
        o = False
        while(not o):
            msg = self.receive()
            if msg != None:
                print("received: " + msg)
                o = True



if __name__ == '__main__':
    q = mp.Queue()

    w = Wrapper(q)
    s = Slicer(w.send)

    p = mp.Process(target=w.receiver, args=())

    p.start()

    s.start()
    
    

