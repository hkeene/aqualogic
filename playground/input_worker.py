FRAME_DLE = b'\x10'
FRAME_STX = b'\x02'
FRAME_ETX = b'\x03'

FRAME_START = FRAME_DLE + FRAME_STX
FRAME_END   = FRAME_DLE + FRAME_ETX

frame = bytearray()

with open("log.bin", "rb") as f:

    while True: #Will break out of this once the file ends
        #First prime the bytearray with two reads
        frame += f.read(2)
        #Iterate over frame until it is the start
        while frame != FRAME_START:
            print("error")
            print(frame)
            frame.pop(0)
            frame += f.read(1)

        while not frame.endswith(FRAME_END):
            frame += f.read(1)

        #Push frame to queue for processing
        print(frame)
        frame.clear()
