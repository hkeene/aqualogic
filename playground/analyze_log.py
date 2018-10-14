FRAME_DLE = b'\x10'
FRAME_STX = b'\x02'
FRAME_ETX = b'\x03'

FRAME_START = FRAME_DLE + FRAME_STX
FRAME_END   = FRAME_DLE + FRAME_ETX

FRAME_TYPE_KEEP_ALIVE = b'\x10\x02\x01\x01\x00\x14\x10\x03'

frame = bytearray()

remove_ca = True

with open("toggle_pool_lights.bin", "rb") as f:

    while True: #Will break out of this once the file ends
        #First prime the bytearray with two reads
        frame += f.read(2)
        #Iterate over frame until it is the start
        while frame != FRAME_START:
            frame.pop(0)
            frame += f.read(1)

        while not frame.endswith(FRAME_END):
            frame += f.read(1)

        #Push frame to queue for processing
        if (frame != FRAME_TYPE_KEEP_ALIVE) and remove_ca :
            print(frame)
        frame.clear()
