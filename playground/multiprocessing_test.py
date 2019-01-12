import multiprocessing as mp
import signal
import time #this is for testing

def process_serial(to_pool, from_pool, logger_q, stop_event):
    logger_q.put('Starting serial process')
    while not stop_event.is_set():
        time.sleep(0.1)
        logger_q.put('Hello from serial process')
    logger_q.put('Stopping serial process')
    
class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True

if __name__ == '__main__':

    killer = GracefulKiller()
    ctx = mp.get_context('spawn')
    logger_q = ctx.Queue()
    to_pool = ctx.Queue()
    from_pool = ctx.Queue()
    stop_event = ctx.Event()
    p =  mp.Process(target=process_serial, args=(to_pool,from_pool,logger_q,stop_event,))
    p.start()
    # print(q.get())
    # print(q.get())
 
    
    while True:
        if not logger_q.empty():
            print(logger_q.get())
            
        if killer.kill_now:
          break
    stop_event.set()
    print("Ending program")
    p.join()
    while not logger_q.empty():
        print(logger_q.get())
