"""
Copyright (C) 2019 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
 and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""
import struct

from scripts.refibroker import Outgoing

"""
Just a thin wrapper around a socket.
It allows us to keep some other info along with it.
"""


import socket
import threading
import logging

from ibapi.common import * # @UnusedWildImport
from ibapi.errors import * # @UnusedWildImport


#TODO: support SSL !!

logger = logging.getLogger(__name__)

def make_msg(text) -> bytes:
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


def read_msg(buf:bytes) -> tuple:
    """ first the size prefix and then the corresponding msg payload """
    if len(buf) < 4:
        return (0, "", buf)
    size = struct.unpack("!I", buf[0:4])[0]
    logger.debug("read_msg: size: %d", size)
    if len(buf) - 4 >= size:
        text = struct.unpack("!%ds" % size, buf[4:4+size])[0]
        return (size, text, buf[4+size:])
    else:
        return (size, "", buf)


def read_fields(buf:bytes) -> tuple:

    if isinstance(buf, str):
        buf = buf.encode()

    """ msg payload is made of fields terminated/separated by NULL chars """
    fields = buf.split(b"\0")

    return tuple(fields[0:-1])   #last one is empty; this may slow dow things though, TODO


class LightConnection(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.wrapper = None
        self.lock = threading.Lock()

    def connect(self):
        try:
            self.socket = socket.socket()
        #TODO: list the exceptions you want to catch
        except socket.error:
            if self.wrapper:
                self.wrapper.error(NO_VALID_ID, FAIL_CREATE_SOCK.code(), FAIL_CREATE_SOCK.msg())

        try:
            self.socket.connect((self.host, self.port))
        except socket.error:
            if self.wrapper:
                self.wrapper.error(NO_VALID_ID, CONNECT_FAIL.code(), CONNECT_FAIL.msg())

        self.socket.settimeout(1)   #non-blocking

    def disconnect(self):
        self.lock.acquire()
        try:
            if self.socket is not None:
                logger.debug("disconnecting")
                self.socket.close()
                self.socket = None
                logger.debug("disconnected")
                if self.wrapper:
                    self.wrapper.connectionClosed()
        finally:
            self.lock.release()

    def is_connected(self):
        return self.socket is not None

    def send_msg(self, msg):

        logger.debug("acquiring lock")
        self.lock.acquire()
        logger.debug("acquired lock")
        if not self.is_connected():
            logger.debug("sendMsg attempted while not connected, releasing lock")
            self.lock.release()
            return 0
        try:
            nSent = self.socket.send(msg)
        except socket.error:
            logger.debug("exception from sendMsg %s", sys.exc_info())
            raise
        finally:
            logger.debug("releasing lock")
            self.lock.release()
            logger.debug("release lock")

        logger.debug("sendMsg: sent: %d", nSent)

        return nSent

    def recv_msg(self):
        if not self.is_connected():
            logger.debug("recvMsg attempted while not connected, releasing lock")
            return b""
        try:
            buf = self._recv_all_msg()
            # receiving 0 bytes outside a timeout means the connection is either
            # closed or broken
            if len(buf) == 0:
                logger.debug("socket either closed or broken, disconnecting")
                self.disconnect()
        except socket.timeout:
            logger.debug("socket timeout from recvMsg %s", sys.exc_info())
            buf = b""
        else:
            pass

        return buf

    def _recv_all_msg(self):
        cont = True
        allbuf = b""

        while cont and self.socket is not None:
            buf = self.socket.recv(4096)
            allbuf += buf
            logger.debug("len %d raw:%s|", len(buf), buf)

            if len(buf) < 4096:
                cont = False

        return allbuf

