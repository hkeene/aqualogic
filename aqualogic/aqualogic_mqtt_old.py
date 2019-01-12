"""
This is the main program for the Aqualogic inteface. It is meant to run as a
systemd daemon. It can also be used stand-alone from the command line.
An example systemd.service file is included and can be used to start and stop
the service.

This program starts the following multiprocessing threads:
- PoolCntl      This thread connects the RS485 interface to the AquaLogic controller
                It monitors the serial stream for data packets and puts those packets
                on the from_pool queue for decoding in the PoolState thread
                It also monitors the to_pool queue and sends those commands to the
                serial interface after a detected keep-alive packet.
                This thread does not monitor the state of the pool controller, or
                handle resending data if it was not received.
- PoolState     This thread connects to the mqtt interface to Home Assistant (or other
                mqtt based home controller). It monitors the mqtt interface for state
                change requests and updates the state as requested. These state
                change requests will create a command to the PoolCntl thread via the
                to_pool queue.
                It also monitors the from_pool queue and determines if the incoming
                packets indicate a state change from the pool controller. If the
                state has changed it publishes the change to the mqtt interfac.
- ThreadedLogger This thread creates a single log file that can be used by both
                worker threads. It is also used by aqualogic_mqtt for logging.

Required arguments:
-m --mqtt       The address to the mqtt server to use for the interface
-s --serial     The device address to use as the serial interface to the Aqualogic controller
-l --log_file   Path for the desired log file

"""
import argparse
from core import PoolState, PoolCntl, ThreadedLogger, GracefulKiller
from multiprocessing import Process, Queue
import time


def main():
    print("Hello from main")
    ser = '/dev/ttyUSB0'

    to_pool = Queue()
    from_pool = Queue()
    logger = Queue()

    pool_cntl = PoolCntl(ser, to_pool, from_pool, logger)
    killer = GracefulKiller()

    p = Process(target=pool_cntl.process)
    p.start
    p.join
    print("Type Cntl-C to close program")
    while True:
        if not logger.empty():
            print(logger.get())
        time.sleep(0.1)
        if killer.kill_now:
          break

    print ("End of the program. I was killed gracefully")

if __name__ == '__main__':
    main()
    # q = Queue()
    # p = Process(target=f, args=(q,))
    # p.start()
    # print(q.get())    # prints "[42, None, 'hello']"
    # p.join()