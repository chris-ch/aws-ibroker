import struct
import sys
from typing import Tuple

from iblight.lightconnection import logger
from iblight.refibroker import Outgoing

UNSET_INTEGER = 2 ** 31 - 1
UNSET_DOUBLE = sys.float_info.max


def make_msg(text: str) -> bytes:
    """ adds the length prefix """
    msg = struct.pack("!I%ds" % len(text), len(text), str.encode(text))
    return msg


def make_field(val) -> str:
    """ adds the NULL string terminator """

    if val is None:
        raise ValueError("Cannot send None to TWS")

    if type(val) is Outgoing:
        val = val.value

    # bool type is encoded as int
    if type(val) is bool:
        val = int(val)

    field = str(val) + '\0'
    return field


def make_field_handle_empty(val) -> str:
    if val is None:
        raise ValueError("Cannot send None to TWS")

    if UNSET_INTEGER == val or UNSET_DOUBLE == val:
        val = ""

    return make_field(val)


def read_msg(buf: bytes) -> Tuple[int, str, bytes]:
    """ first the size prefix and then the corresponding msg payload """
    if len(buf) < 4:
        return 0, "", buf
    size = struct.unpack("!I", buf[0:4])[0]
    logger.debug("read_msg: size: %d", size)
    if len(buf) - 4 >= size:
        text = struct.unpack("!%ds" % size, buf[4:size + 4])[0]
        return size, text, buf[size + 4:]
    else:
        return size, "", buf


def read_fields(buf: str) -> Tuple[bytes]:
    if isinstance(buf, str):
        buf = buf.encode()

    """ msg payload is made of fields terminated/separated by NULL chars """
    fields = buf.split(b"\0")

    return tuple(fields[0:-1])   #last one is empty; this may slow dow things though, TODO
