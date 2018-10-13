"""A library to interface with a Hayward/Goldline AquaLogic/ProLogic
pool controller."""

class PoolCntl():
    """ Hayward/Goldline AquaLogic/ProLogic pool controller.
        This thread connects the RS485 interface to the AquaLogic controller
        It monitors the serial stream for data packets and puts those packets
        on the from_pool queue for decoding in the PoolState thread
        It also monitors the to_pool queue and sends those commands to the
        serial interface after a detected keep-alive packet.
        This thread does not monitor the state of the pool controller, or
        handle resending data if it was not received.
    """
    def __init__(self, ser, to_pool, from_pool, logger):
        self._serial = ser
        self._to_pool = to_pool
        self._from_pool = from_pool
        self._logger = logger

    def connect(self, host, port):
        """Connects via a RS-485 to Ethernet adapter."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self._reader = sock.makefile(mode='rb')
        self._writer = sock.makefile(mode='wb')
