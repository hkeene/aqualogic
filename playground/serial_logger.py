import serial, time, io, datetime
from serial import Serial

ser = serial.Serial(
    port = '/dev/ttyUSB0',\
    baudrate = 19200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_TWO,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)


print("Connected to: " + ser.portstr)

#f = open("log.bin", "wb")

for x in range(100):
    y = ser.read(1)
    print(y)
    #f.write(y)

ser.close()
#f.close()
