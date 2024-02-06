import multiprocessing as mp
import time, pickle


def send(mem):
    mem["msg"] = "something"
    


if __name__ == '__main__':
    manager = mp.Manager()
    d = manager.dict()

    p = mp.Process(target=send, args=(d,))
    p.start()
    time.sleep(1)

    print(d)
    manager.shutdown()