import serial
import pickle

frame = bytearray()
data = list()

BYTES_TO_READ = 2000
log_name = "/home/hkeene/pool/aqualogic/playground/logs/raw.bin"

if __name__ == '__main__':

    ser = serial.Serial(
        port = '/dev/ttyUSB0',\
        baudrate = 19200)
    print("Connected to: " + ser.portstr)

    #Prime the prev for the first time loop
    read = ser.read(BYTES_TO_READ)
    with open (log_name, "wb") as fp:
        pickle.dump(read, fp)

    ser.close()
