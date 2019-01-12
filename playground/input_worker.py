FRAME_DLE = b'\x10'
FRAME_STX = b'\x02'
FRAME_ETX = b'\x03'

FRAME_TYPE_KEEP_ALIVE = b'\x10\x02\x01\x01\x00\x14\x10\x03'

FRAME_START = FRAME_DLE + FRAME_STX
FRAME_END   = FRAME_DLE + FRAME_ETX

frame = bytearray()

log_name = "/home/hkeene/pool/aqualogic/playground/logs/raw.bin"

with open(log_name, "rb") as ser:
    stop_event = False
    # frame_cnt = 0
    #Prime the prev for the first time loop
    prev = ser.read(1)
    curr = ser.read(1)
#    while not stop_event:
    for x in range(500):
        if (prev == FRAME_DLE) & (curr == FRAME_STX):
            #Start of new frame marker
            frame = bytearray() # reset frame
            frame += prev 
            end_frame = False
            while (not end_frame) & (not stop_event):
                if (prev == FRAME_DLE) & (curr == FRAME_ETX):
                    end_frame = True
                    frame += curr
                    prev = curr
                    curr = ser.read(1)

                else:
                    frame += curr
                    prev = curr
                    curr = ser.read(1)
            if frame == FRAME_TYPE_KEEP_ALIVE:
                pass #We would print here
            else:
                #Not a keep alive so we should send this to the queue
                print(frame) #Print when it gets to the end
        else:
            prev = curr
            curr = ser.read(1)









#     frame = bytearray(FRAME_TYPE_KEEP_ALIVE) # Prime the frame in case we find a packet start at the very first
    
#     # frame_cnt = 0
#     #Prime the prev for the first time loop
#     prev = ser.read(1)
#     while True:
#         curr = ser.read(1)
#         if (prev == FRAME_DLE) & (curr == FRAME_STX):
#             #Start of new frame marker
            
#             final_frame = frame[:-1]
#             print(final_frame)
# #            from_pool.put(frame) #append previous frame to list to save
#             frame = bytearray()
#             frame += prev
#             frame += curr
#             prev = curr
#         else:
#             frame += curr
#             prev = curr
