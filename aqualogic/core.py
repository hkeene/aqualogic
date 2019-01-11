"""A library to interface with a Hayward/Goldline AquaLogic/ProLogic
pool controller."""

import sys
import signal

class PoolCntl():
    """ Hayward/Goldline AquaLogic/ProLogic pool controller.
        This thread connects the RS485 interface to the AquaLogic controller
        It monitors the serial stream for data packets and puts those packets
        on the from_pool queue for decoding in the PoolState thread
        It also monitors the to_pool queue and sends those commands to the
        serial interface after a detected keep-alive packet.
        This thread does not monitor the state of the pool controller, or
        handle resending data if it was not received.
    """
    def __init__(self, ser, to_pool, from_pool, logger):
        self._serial_addr = ser
        self._to_pool = to_pool
        self._from_pool = from_pool
        self._logger = logger

    def process(self):
        """ Process incoming serial stream and place them on the from_pool queue,
            and transmit packets to the pool when they are placed in the to_pool queue."""

        self._logger.put("Hello from serial process")
        
 
    #     killer = GracefulKiller()
    #     ser = serial.Serial(
    #         port = self._serial_addr,\
    #         baudrate = 19200)
    
    #     print("Connected to: " + ser.portstr)
    
    #     while True:
    #         #First prime the bytearray with two reads
    #         frame += ser.read(2)
    #         #Iterate over frame until it is the start
    #         while frame != FRAME_START:
    #           # print("missed start frame")
    #             frame.pop(0)
    #             frame += ser.read(1)
    
    #         while not frame.endswith(FRAME_END):
    #             frame += ser.read(1)
    
    #         #Push frame to queue for processing
    #         if (frame == FRAME_TYPE_KEEP_ALIVE) and q:
    #             #print("sending light command")
    #             x = q.pop(0)
    #             ser.write(x)
    #             print("Sending command")
    #             print(x)
    # #            print(FRAME_LIGHTS)
    # #            do_once = False
    #         f.write(frame)
    #         frame.clear()

    #         if killer.kill_now:
    #           break
    
    #     print ("End of the program. I was killed gracefully")
    
    #     ser.close()
    #     f.close()

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True

def _append_data(self, frame, data):
    for byte in data:
        frame += byte
        if byte == self.FRAME_DLE:
            frame += 0

class PoolState():
    '''this is the pool state class'''

class ThreadedLogger():
    '''this is the threaded logger class'''