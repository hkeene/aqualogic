import serial
import signal

FRAME_DLE = b'\x10'
FRAME_STX = b'\x02'
FRAME_ETX = b'\x03'

FRAME_START = FRAME_DLE + FRAME_STX
FRAME_END   = FRAME_DLE + FRAME_ETX

FRAME_TYPE_KEY_EVENT = b'\x00\x03'
LIGHTS = b'\x00\x01'

#FRAME_LIGHTS = b'\x10\x02\x01\x02\x68\x00\xfe\x01\x00\x00\x00\x00\x01\x7c\x10\x03'
FRAME_TYPE_KEEP_ALIVE = b'\x10\x02\x01\x01\x00\x14\x10\x03'

FRAME_LIGHTS = b'\x10\x02\x00\x02\x00\x01\x00\x00\x00\x01\x00\x00\x00\x16\x10\x03'

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

frame = bytearray()

if __name__ == '__main__':
    # Create frame to send
    lights = bytearray()
    lights += FRAME_DLE
    lights += FRAME_STX

    lights += FRAME_TYPE_KEY_EVENT

    lights += LIGHTS
    lights += LIGHTS

    crc = 0
    for byte in lights:
        crc += byte

    lights += crc.to_bytes(2, byteorder='big')

    lights += FRAME_DLE
    lights += FRAME_ETX

    print(lights)


    do_once = True
    killer = GracefulKiller()
    ser = serial.Serial(
        port = '/dev/ttyUSB0',\
        baudrate = 19200)

    print("Connected to: " + ser.portstr)

    f = open("log.bin", "wb")

    print("Opened log file")
    print("Type CTNL-C to stop")

    while True:
        #First prime the bytearray with two reads
        frame += ser.read(2)
        #Iterate over frame until it is the start
        while frame != FRAME_START:
           # print("missed start frame")
            frame.pop(0)
            frame += ser.read(1)

        while not frame.endswith(FRAME_END):
            frame += ser.read(1)

        #Push frame to queue for processing
        if (frame == FRAME_TYPE_KEEP_ALIVE) and do_once :
            #print("sending light command")
            ser.write(FRAME_LIGHTS)
            print("sending light command")
            print(FRAME_LIGHTS)
            do_once = False
        f.write(frame)
        frame.clear()



        if killer.kill_now:
          break

    print ("End of the program. I was killed gracefully")

    ser.close()
    f.close()
