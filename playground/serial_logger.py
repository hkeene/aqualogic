import serial
import signal

FRAME_DLE = b'\x10'
FRAME_STX = b'\x02'
FRAME_ETX = b'\x03'

FRAME_START = FRAME_DLE + FRAME_STX
FRAME_END   = FRAME_DLE + FRAME_ETX

class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        self.kill_now = True

frame = bytearray()

if __name__ == '__main__':
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
            #print(frame)
            frame.pop(0)
            frame += ser.read(1)

        while not frame.endswith(FRAME_END):
            frame += ser.read(1)

        #Push frame to queue for processing
        f.write(frame)
        frame.clear()



        if killer.kill_now:
          break

    print ("End of the program. I was killed gracefully")

    ser.close()
    f.close()
