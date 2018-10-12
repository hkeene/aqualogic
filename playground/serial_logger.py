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

seq = bytearray()

for x in range (100):
    seq.append(ser.read(1))

ser.close()

f = open("log.bin", "x")
f.write(seq)

f.close()
