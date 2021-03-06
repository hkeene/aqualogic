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
import paho.mqtt.client as mqtt
import json


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

class MyLogger():
    def __init__(self, logging_flag):
        self.logging_flag = logging_flag
    def log(self,log_text):
        if self.logging_flag:
            print(log_text)

class AquaLogic():
    """Hayward/Goldline AquaLogic/ProLogic pool controller."""
    FRAME_DLE = b'\x10'
    FRAME_STX = b'\x02'
    FRAME_ETX = b'\x03'
    
    FRAME_START = FRAME_DLE + FRAME_STX
    FRAME_END   = FRAME_DLE + FRAME_ETX
    
    FRAME_TYPE_DISPLAY_UPDATE = b'\x01\x03'
    FRAME_TYPE_LEDS = b'\x01\x02'

    def __init__(self):
        self.air_temp = None
        self.pool_temp = None
        self.spa_temp = None
        self.salt_level = None
        self.day_of_week = None
        self.time = None
        self.topics =   {"pool_temperature_addr"    : "pool/pool_temperature",
                         "spa_temperature_addr"     : "pool/spa_temperature",
                         "outside_temperature_addr" : "pool/outside_temperature",
                         "day_of_week_addr"         : "pool/day_of_week",
                         "time_addr"                : "pool/time" }
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    def process(self, frame, mqtt_client, logger):
        #Split frame into parts
        frame_type = frame[2:4]
        frame_content = frame[4:-5]
        frame_crc = frame[-5:-2]

        # Check for correct headers and footers
        if not self.hdr_ftr_correct(frame):
            logger.log("Bad header & footer")
            logger.log(frame)
            return
        
        # Check for correct CRC
        if not self.crc_correct(frame_content, frame_crc):
            logger.log("Bad CRC")
            logger.log(frame)
            return
    
        if frame_type == self.FRAME_TYPE_DISPLAY_UPDATE:
            logger.log("Display update frame")
            parts = frame_content.decode('latin-1').split()
            logger.log(parts)
            try:
                if parts[0] == 'Pool' and parts[1] == 'Temp':
                    # Pool Temp <temp>°[C|F]
                    value = int(parts[2][:-2])
                    if self.pool_temp != value:
                        self.pool_temp = value
                        logger.log("Pool temp")
                        logger.log(self.pool_temp)
                        mqtt_client.publish(controller.topics["pool_temperature_addr"], 
                           json.dumps({"pool_temperature": self.pool_temp}, indent=4), 1)

                # elif parts[0] == 'Spa' and parts[1] == 'Temp':
                #     # Spa Temp <temp>°[C|F]
                #     value = int(parts[2][:-2])
                #     logger.log("Spa temp")
                #     logger.log(value)
                    

                    # if self._spa_temp != value:
                    #     self._spa_temp = value
                    #     self._is_metric = parts[2][-1:] == 'C'
                    #     data_changed_callback(self)
                elif parts[0] == 'Air' and parts[1] == 'Temp':
                    # Air Temp <temp>°[C|F]
                    value = int(parts[2][:-2])

                    if self.air_temp != value:
                        self.air_temp = value
                        logger.log("Air temp")
                        logger.log(self.air_temp)
                        mqtt_client.publish(controller.topics["outside_temperature_addr"], 
                           json.dumps({"outside_temperature": self.air_temp}, indent=4), 1)

                elif parts[0] in self.days:  
                    #Time of day and day of week. Using this as a heartbeat
                    day = parts[0]
                    time = parts[1].replace('º',':')
                    if self.day_of_week != day:
                        self.day_of_week = day
                        logger.log("Day updated")
                        logger.log(self.day_of_week)
                        mqtt_client.publish(controller.topics["day_of_week_addr"], 
                           json.dumps({"day_of_week": self.day_of_week}, indent=4), 1)
                    if self.time != time:
                        self.time = time
                        logger.log("Time updated")
                        logger.log(self.time)
                        mqtt_client.publish(controller.topics["time_addr"], 
                           json.dumps({"time": self.time}, indent=4), 1)


                # elif parts[0] == 'Pool' and parts[1] == 'Chlorinator':
                #     # Pool Chlorinator <value>%
                #     value = int(parts[2][:-1])
                #     if self._pool_chlorinator != value:
                #         self._pool_chlorinator = value
                #         data_changed_callback(self)
                # elif parts[0] == 'Spa' and parts[1] == 'Chlorinator':
                #     # Spa Chlorinator <value>%
                #     value = int(parts[2][:-1])
                #     if self._spa_chlorinator != value:
                #         self._spa_chlorinator = value
                #         data_changed_callback(self)
                elif parts[0] == 'Salt' and parts[1] == 'Level':
                    # Salt Level <value> [g/L|PPM|
                    value = float(parts[2])
                    logger.log("Salt Level")
                    logger.log(value)

                    # if self._salt_level != value:
                    #     self._salt_level = value
                    #     self._is_metric = parts[3] == 'g/L'
                    #     data_changed_callback(self)
                # elif parts[0] == 'Check' and parts[1] == 'System':
                #     # Check System <msg>
                #     value = ' '.join(parts[2:])
                #     if self._check_system_msg != value:
                #         self._check_system_msg = value
                #         data_changed_callback(self)
            except ValueError:
                pass
            
            
            
            
            
        elif frame_type == self.FRAME_TYPE_LEDS:
            logger.log("LED update")
            logger.log(frame_content)
        else:
            logger.log("Unknown frame type")
            logger.log(frame_type)
            logger.log(frame_content)

    
    def on_connect(self, client, data, flags, rc):
        for key, addr in self.topics.items():
            client.subscribe(addr, 1)

    def hdr_ftr_correct(self, frame):
        if (frame[0:2] == self.FRAME_START) & (frame[-2:] == self.FRAME_END):
            return True
        else:
            return False

    def crc_correct(self, frame_content, frame_crc):
        return True #Not sure why this isn't working yet...
    
        # # Verify CRC
        # frame_crc_int = int.from_bytes(frame_crc, byteorder='big')
    
        # calculated_crc = int.from_bytes(FRAME_DLE, byteorder='big') + int.from_bytes(FRAME_STX, byteorder='big')
        # for byte in frame:
        #     calculated_crc = calculated_crc + byte
    
        # if frame_crc_int != calculated_crc:
        #     return False
        # else:
        #     return True


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
    log_name = "/home/hkeene/pool/aqualogic/playground/logs/messages_from_pool2.bin"
    log_chk = False #set to true to log received data
    data = list()

    serial_addr = '/dev/ttyUSB0'

    controller = AquaLogic()
    logger = MyLogger(log_chk)
    
    broker="192.168.1.100"
    port=1883
    username="hkeene"
    password="homer4MQTT!"

    mqtt_client = mqtt.Client("Pool1")
    mqtt_client.on_connect = controller.on_connect
    #client.on_message = on_message
    mqtt_client.username_pw_set(username, password)
    logger.log("Connecting to MQTT server")
    mqtt_client.connect(broker, port, 60)
    mqtt_client.loop_start()    
    
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
            controller.process(frame, mqtt_client, logger)

#            print(frame)
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
    
    mqtt_client.disconnect()
