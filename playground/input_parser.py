import pickle
import binascii

FRAME_DLE = b'\x10'
FRAME_STX = b'\x02'
FRAME_ETX = b'\x03'

FRAME_START = FRAME_DLE + FRAME_STX
FRAME_END   = FRAME_DLE + FRAME_ETX

FRAME_TYPE_DISPLAY_UPDATE = b'\x01\x03'
FRAME_TYPE_LEDS = b'\x01\x02'


def hdr_ftr_correct(frame):
    if (frame[0:2] == FRAME_START) & (frame[-2:] == FRAME_END):
        return True
    else:
        return False

def crc_correct(frame_content, frame_crc):
    return True #Not sure why this isn't working yet...

    # # Verify CRC
    # frame_crc_int = int.from_bytes(frame_crc, byteorder='big')

    # calculated_crc = int.from_bytes(FRAME_DLE, byteorder='big') + int.from_bytes(FRAME_STX, byteorder='big')
    # for byte in frame:
    #     calculated_crc = calculated_crc + byte

    # if frame_crc_int != calculated_crc:
    #     return False
    # else:
    #     return True
    
def logger(text):
    print(text)

log_name = "/home/hkeene/pool/aqualogic/playground/logs/messages_from_pool.bin"

if __name__ == '__main__':

    with open(log_name, 'rb') as fp:
        items = pickle.load(fp)
    
    for frame in items:
        #Split frame into parts
        frame_type = frame[2:4]
        frame_content = frame[4:-5]
        frame_crc = frame[-5:-2]

        # Check for correct headers and footers
        if not hdr_ftr_correct(frame):
            logger("Bad header & footer")
            logger(frame)
            continue
        
        # Check for correct CRC
        if not crc_correct(frame_content, frame_crc):
            logger("Bad CRC")
            logger(frame)
            continue
    
        if frame_type == FRAME_TYPE_DISPLAY_UPDATE:
            logger("Display update frame")
            parts = frame_content.decode('latin-1').split()
            logger(parts)
        elif frame_type == FRAME_TYPE_LEDS:
            logger("LED update")
            logger(frame_content)
        else:
            logger("Unknown frame type")
            logger(frame_type)
            logger(frame_content)



    # if frame_type == self.FRAME_TYPE_KEEP_ALIVE:
    #     # Keep alive
    #     # If a frame has been queued for transmit, send it.
    #     if not self._send_queue.empty():
    #         data = self._send_queue.get(block=False)
    #         self._writer.write(data['frame'])
    #         self._writer.flush()
    #         _LOGGER.info('Sent: %s', binascii.hexlify(data['frame']))

    #         try:
    #             if data['desired_states'] is not None:
    #                 # Set a timer to verify the state changes
    #                 # Wait 2 seconds as it can take a while for
    #                 # the state to change.
    #                 Timer(2.0, self._check_state, [data]).start()
    #         except KeyError:
    #             pass

    #     continue
    # elif frame_type == self.FRAME_TYPE_KEY_EVENT:
    #     _LOGGER.info('Key: %s', binascii.hexlify(frame))
    # elif frame_type == self.FRAME_TYPE_LEDS:
    #     _LOGGER.debug('LEDs: %s', binascii.hexlify(frame))
    #     # First 4 bytes are the LEDs that are on;
    #     # second 4 bytes_ are the LEDs that are flashing
    #     states = int.from_bytes(frame[0:4], byteorder='little')
    #     flashing_states = int.from_bytes(frame[4:8],
    #                                      byteorder='little')
    #     states |= flashing_states
    #     if (states != self._states
    #             or flashing_states != self._flashing_states):
    #         self._states = states
    #         self._flashing_states = flashing_states
    #         data_changed_callback(self)
    # elif frame_type == self.FRAME_TYPE_PUMP_SPEED_REQUEST:
    #     value = int.from_bytes(frame[0:2], byteorder='big')
    #     _LOGGER.debug('Pump speed request: %d%%', value)
    #     if self._pump_speed != value:
    #         self._pump_speed = value
    #         data_changed_callback(self)
    # elif frame_type == self.FRAME_TYPE_PUMP_STATUS:
    #     # Pump status messages sent out by Hayward VSP pumps
    #     self._multi_speed_pump = True
    #     speed = frame[2]
    #     # Power is in BCD
    #     power = ((((frame[3] & 0xf0) >> 4) * 1000)
    #              + (((frame[3] & 0x0f)) * 100)
    #              + (((frame[4] & 0xf0) >> 4) * 10)
    #              + (((frame[4] & 0x0f))))
    #     _LOGGER.debug('Pump speed: %d%%, power: %d watts',
    #                   speed, power)
    #     if self._pump_power != power:
    #         self._pump_power = power
    #         data_changed_callback(self)
    # elif frame_type == self.FRAME_TYPE_DISPLAY_UPDATE:
    #     parts = frame.decode('latin-1').split()
    #     _LOGGER.debug('Display update: %s', parts)

    #     try:
    #         if parts[0] == 'Pool' and parts[1] == 'Temp':
    #             # Pool Temp <temp>°[C|F]
    #             value = int(parts[2][:-2])
    #             if self._pool_temp != value:
    #                 self._pool_temp = value
    #                 self._is_metric = parts[2][-1:] == 'C'
    #                 data_changed_callback(self)
    #         elif parts[0] == 'Spa' and parts[1] == 'Temp':
    #             # Spa Temp <temp>°[C|F]
    #             value = int(parts[2][:-2])
    #             if self._spa_temp != value:
    #                 self._spa_temp = value
    #                 self._is_metric = parts[2][-1:] == 'C'
    #                 data_changed_callback(self)
    #         elif parts[0] == 'Air' and parts[1] == 'Temp':
    #             # Air Temp <temp>°[C|F]
    #             value = int(parts[2][:-2])
    #             if self._air_temp != value:
    #                 self._air_temp = value
    #                 self._is_metric = parts[2][-1:] == 'C'
    #                 data_changed_callback(self)
    #         elif parts[0] == 'Pool' and parts[1] == 'Chlorinator':
    #             # Pool Chlorinator <value>%
    #             value = int(parts[2][:-1])
    #             if self._pool_chlorinator != value:
    #                 self._pool_chlorinator = value
    #                 data_changed_callback(self)
    #         elif parts[0] == 'Spa' and parts[1] == 'Chlorinator':
    #             # Spa Chlorinator <value>%
    #             value = int(parts[2][:-1])
    #             if self._spa_chlorinator != value:
    #                 self._spa_chlorinator = value
    #                 data_changed_callback(self)
    #         elif parts[0] == 'Salt' and parts[1] == 'Level':
    #             # Salt Level <value> [g/L|PPM|
    #             value = float(parts[2])
    #             if self._salt_level != value:
    #                 self._salt_level = value
    #                 self._is_metric = parts[3] == 'g/L'
    #                 data_changed_callback(self)
    #         elif parts[0] == 'Check' and parts[1] == 'System':
    #             # Check System <msg>
    #             value = ' '.join(parts[2:])
    #             if self._check_system_msg != value:
    #                 self._check_system_msg = value
    #                 data_changed_callback(self)
    #     except ValueError:
    #         pass
    # else:
    #     _LOGGER.info('Unknown frame: %s %s',
    #                  binascii.hexlify(frame_type),
    #                  binascii.hexlify(frame))
