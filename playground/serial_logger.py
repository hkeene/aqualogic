import serial

#ser = serial.Serial(
#    port = '/dev/ttyUSB0',\
#    baudrate = 19200,\
#    parity=serial.PARITY_NONE,\
#    stopbits=serial.STOPBITS_TWO,\
#    bytesize=serial.EIGHTBITS)

#ser = serial.Serial('/dev/ttyUSB0')

ser = serial.Serial(
    port = '/dev/ttyUSB0',\
    baudrate = 19200)
#    parity=serial.PARITY_NONE,\
#    stopbits=serial.STOPBITS_TWO,\
#    bytesize=serial.EIGHTBITS)

print("Connected to: " + ser.portstr)

f = open("log.bin", "wb")

for x in range(4000):
    y = ser.read(1)
    #print(y)
    f.write(y)

ser.close()
f.close()
