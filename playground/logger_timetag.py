import serial
import datetime
import pickle

FRAME_DLE = b'\x10'
FRAME_STX = b'\x02'
FRAME_ETX = b'\x03'

FRAME_START = FRAME_DLE + FRAME_STX
FRAME_END   = FRAME_DLE + FRAME_ETX

frame = bytearray()
data = list()

BYTES_TO_READ = 2000
log_name = "/home/hkeene/pool/aqualogic/playground/logs/31_pool_pump_off.bin"

if __name__ == '__main__':

    ser = serial.Serial(
        port = '/dev/ttyUSB0',\
        baudrate = 19200)
    print("Connected to: " + ser.portstr)

    #Prime the prev for the first time loop
    prev = ser.read(1)
    for x in range(BYTES_TO_READ):
        curr = ser.read(1)
        if (prev == FRAME_DLE) & (curr == FRAME_STX):
            #Start of new frame marker
            data.append(frame) #append previous frame to list to save
            data.append(datetime.datetime.now())  #append time stamp of new frame
            frame = bytearray()
            frame += prev
            frame += curr
            prev = curr
        else:
            frame += curr
            prev = curr


    with open (log_name, "wb") as fp:
        pickle.dump(data, fp)

    ser.close()
