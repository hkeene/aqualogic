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
import time
import multiprocessing as mp
import signal
import serial
import time #this is for testing
import pickle


FRAME_DLE = b'\x10'
FRAME_STX = b'\x02'
FRAME_ETX = b'\x03'

FRAME_START = FRAME_DLE + FRAME_STX
FRAME_END   = FRAME_DLE + FRAME_ETX

FRAME_TYPE_KEY_EVENT = b'\x00\x03'
LIGHTS = b'\x00\x01'

#FRAME_LIGHTS = b'\x10\x02\x01\x02\x68\x00\xfe\x01\x00\x00\x00\x00\x01\x7c\x10\x03'
FRAME_TYPE_KEEP_ALIVE = b'\x10\x02\x01\x01\x00\x14\x10\x03'
#WATER_ON = b'\x10\x02\x00\x02\x00\x01\x00\x00\x00\x01\x00\x00\x00\x16\x10\x03'
WATER_ON =  b'\x10\x02\x00\x02\x00\x10\x00\x00\x00\x00\x10\x00\x00\x00\x00\x34\x10\x03\x10\x02\x01\x02\x28\x08\x00\x00\x00\x00\x00\x00\x00\x45\x10\x03'
WATER_OFF = b'\x10\x02\x00\x02\x00\x10\x00\x00\x00\x00\x10\x00\x00\x00\x00\x34\x10\x03\x10\x02\x01\x02\x28\x00\x00\x00\x00\x00\x00\x00\x00\x3d\x10\x03'

def process_serial(serial_addr, to_pool, from_pool, logger_q, stop_event):
    logger_q.put('Starting serial process')
    ser = serial.Serial(
        port = serial_addr,\
        baudrate = 19200)

    logger_q.put("Connected to: " + ser.portstr)

    #Prime the prev and curr for the first time loop
    prev = ser.read(1)
    curr = ser.read(1)
    while not stop_event.is_set(): #This main loop finds the start of a frame
        if (prev == FRAME_DLE) & (curr == FRAME_STX):
            #Start of new frame marker
            frame = bytearray() # reset frame
            frame += prev 
            end_frame = False
            while (not end_frame) & (not stop_event.is_set()): #This loop finds the end of the frame
                if (prev == FRAME_DLE) & (curr == FRAME_ETX): #If this is the end of frame then break the loop
                    end_frame = True
                    frame += curr
                    prev = curr
                    curr = ser.read(1)
                else: #Continue looking for end of frame
                    frame += curr
                    prev = curr
                    curr = ser.read(1)
            if frame == FRAME_TYPE_KEEP_ALIVE:
                pass #If transmit queue has something in it then transmit it
            else:
                #The frame is not a keep alive so we should send this to the from_pool queue
                from_pool.put(frame)
        else:
            #Keep searching for start of new frame marker
            prev = curr
            curr = ser.read(1)

    logger_q.put('Stopping serial process')
    ser.close()
    logger_q.put('Serial port closed')

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True

if __name__ == '__main__':
    #Debugging code below. Could turn it into a logging option
    log_name = "/home/hkeene/pool/aqualogic/playground/logs/messages_from_pool.bin"
    log_chk = True #set to true to log received data
    data = list()

    serial_addr = '/dev/ttyUSB0'
    
    killer = GracefulKiller()
    ctx = mp.get_context('spawn')
    logger_q = ctx.Queue()
    to_pool = ctx.Queue()
    from_pool = ctx.Queue()
    stop_event = ctx.Event()
    p =  mp.Process(target=process_serial, args=(serial_addr,to_pool,from_pool,logger_q,stop_event,))
    p.start()
    while True:
        if not logger_q.empty():
            print(logger_q.get())
        if not from_pool.empty():
            frame = from_pool.get()
            print(frame)
            if log_chk:
                data.append(frame)
        if killer.kill_now:
          break
    stop_event.set()
    print("Ending program")
    p.join()
    if log_chk:
        with open (log_name, "wb") as fp:
            pickle.dump(data, fp)
    while not logger_q.empty():
        print(logger_q.get())
