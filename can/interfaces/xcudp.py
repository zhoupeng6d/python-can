"""
This module implements a cu-based M&A udp protocol interface, the purpose is to simulate CAN data transmit-receive.
"""
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from can import typechecking

from copy import deepcopy
import logging
import time
import queue
from threading import RLock
from random import randint

from can import CanError
from can.bus import BusABC
from can.message import Message
import socket

logger = logging.getLogger(__name__)


dlc2len = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]

# Channels are lists of queues, one for each connection
if TYPE_CHECKING:
    # https://mypy.readthedocs.io/en/stable/common_issues.html#using-classes-that-are-generic-in-stubs-but-not-at-runtime
    channels: Dict[Optional[Any], List[queue.Queue[Message]]] = {}
else:
    channels = {}
channels_lock = RLock()


class XcudpBus(BusABC):
    """
    An interface that simulates the XCU's M core UDP protocol
    """

    def __init__(
        self,
        channel: Any = None,
        receive_own_messages: bool = False,
        rx_queue_size: int = 0,
        **kwargs: Any
    ) -> None:
        super().__init__(
            channel=channel, receive_own_messages=receive_own_messages, **kwargs
        )

        # the channel identifier may be an arbitrary object
        self.channel_id = channel
        self.channel_info = "xcu udp {}".format(self.channel_id)
        self._open = True
        self.UDP_IP = "127.0.0.1"
        self.UDP_PORT = 4531
        self.playback_start_time = None

        self.sock = socket.socket(socket.AF_INET, # Internet
                                 socket.SOCK_DGRAM) # UDP
        with channels_lock:

            # Create a new channel if one does not exist
            if self.channel_id not in channels:
                channels[self.channel_id] = []
            self.channel = channels[self.channel_id]

            self.queue: queue.Queue[Message] = queue.Queue(rx_queue_size)
            self.channel.append(self.queue)

    def _check_if_open(self) -> None:
        """Raises CanError if the bus is not open.

        Has to be called in every method that accesses the bus.
        """
        if not self._open:
            raise CanError("Operation on closed bus")

    def _recv_internal(
        self, timeout: Optional[float]
    ) -> Tuple[Optional[Message], bool]:
        self._check_if_open()
        try:
            msg = self.queue.get(block=True, timeout=timeout)
        except queue.Empty:
            return None, False
        else:
            return msg, False

    def datalen(self, len):
        global dlc2len
        return dlc2len[len]+15

    def udpSend(self, data):
        self.sock.sendto(data, (self.UDP_IP, self.UDP_PORT))

    def send(self, msg: Message, timeout: Optional[float] = None) -> None:
        self._check_if_open()
        global dlc2len

        if self.playback_start_time is None:
            self.playback_start_time = time.time()

        # type uint8_t
        b = bytearray(self.datalen(msg.dlc))
        b[0] = 0x00
        # size of frames uint16_t
        b[1] = 0x01
        b[2] = 0x00
        # timestamp uint64_t
        timestamp = self.playback_start_time + msg.timestamp
        millis = int(round(timestamp * 1000))
        b[3:10] = millis.to_bytes(8, 'little')
        # id uint16_t
        b[11:12] = msg.arbitration_id.to_bytes(2, 'little')
        if msg.is_fd:
            b[12] |= 0x10
        # channel uint8_t
        b[13] = msg.channel
        # len uint8_t
        b[14] = dlc2len[msg.dlc]
        # data n-bytes
        b[15:] = msg.data

        #print(f'{millis} {msg.timestamp} {hex(msg.arbitration_id)} {msg.channel} {msg.is_fd} {msg.dlc} {msg.data} ')
        #print(b.hex())

        self.udpSend(b)

        # Add message to all listening on this channel
        all_sent = True
        if not all_sent:
            raise CanError("Could not send message to one or more recipients")

    def shutdown(self) -> None:
        self._check_if_open()
        self._open = False

        with channels_lock:
            self.channel.remove(self.queue)

            # remove if empty
            if not self.channel:
                del channels[self.channel_id]

    @staticmethod
    def _detect_available_configs():
        """
        Returns all currently used channels as well as
        one other currently unused channel.

        .. note::

            This method will run into problems if thousands of
            autodetected buses are used at once.

        """
        with channels_lock:
            available_channels = list(channels.keys())

        # find a currently unused channel
        get_extra = lambda: "channel-{}".format(randint(0, 9999))
        extra = get_extra()
        while extra in available_channels:
            extra = get_extra()

        available_channels += [extra]

        return [
            {"interface": "xcudp", "channel": channel}
            for channel in available_channels
        ]
