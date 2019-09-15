"""
Copyright (C) 2019 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
 and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""

import socket
import sys
import threading
import logging

logger = logging.getLogger(__name__)


class CodeMsgPair:
    def __init__(self, code, msg):
        self.errorCode = code
        self.errorMsg = msg

    def code(self):
        return self.errorCode

    def msg(self):
        return self.errorMsg


NO_VALID_ID = -1

CONNECT_FAIL = CodeMsgPair(502,
                           """Couldn't connect to TWS. Confirm that \"Enable ActiveX and Socket EClients\" 
is enabled and connection port is the same as \"Socket Port\" on the 
TWS \"Edit->Global Configuration...->API->Settings\" menu. Live Trading ports: 
TWS: 7496; IB Gateway: 4001. Simulated Trading ports for new installations 
of version 954.1 or newer:  TWS: 7497; IB Gateway: 4002""")
UPDATE_TWS = CodeMsgPair(503, "The TWS is out of date and must be upgraded.")
NOT_CONNECTED = CodeMsgPair(504, "Not connected")
BAD_LENGTH = CodeMsgPair(507, "Bad message length")
BAD_MESSAGE = CodeMsgPair(508, "Bad message")
FAIL_CREATE_SOCK = CodeMsgPair(520, "Failed to create socket")

"""
Just a thin wrapper around a socket.
It allows us to keep some other info along with it.
"""


# TODO: support SSL !!


class LightConnection(object):

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket = None
        self._wrapper = None  # PROBABLY not used
        self._lock = threading.Lock()

    def connect(self):
        try:
            self._socket = socket.socket()
        # TODO: list the exceptions you want to catch
        except socket.error:
            if self._wrapper:
                self._wrapper.error(NO_VALID_ID, FAIL_CREATE_SOCK.code(), FAIL_CREATE_SOCK.msg())

        try:
            self._socket.connect((self._host, self._port))
        except socket.error:
            if self._wrapper:
                self._wrapper.error(NO_VALID_ID, CONNECT_FAIL.code(), CONNECT_FAIL.msg())

        self._socket.settimeout(1)  # non-blocking

    def disconnect(self):
        self._lock.acquire()
        try:
            if self._socket is not None:
                logger.debug("disconnecting")
                self._socket.close()
                self._socket = None
                logger.debug("disconnected")
                if self._wrapper:
                    self._wrapper.connectionClosed()
        finally:
            self._lock.release()

    def is_connected(self):
        return self._socket is not None

    def send_msg(self, msg: bytes) -> int:
        logger.debug("acquiring lock")
        self._lock.acquire()
        logger.debug("acquired lock")
        if not self.is_connected():
            logger.debug("send_msg attempted while not connected, releasing lock")
            self._lock.release()
            return 0
        try:
            status = self._socket.send(msg)
        except socket.error:
            logger.debug("exception from sendMsg %s", sys.exc_info())
            raise
        finally:
            logger.debug("releasing lock")
            self._lock.release()
            logger.debug("release lock")

        logger.debug("send_msg: sent: %d", status)

        return status

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

        while cont and self._socket is not None:
            buf = self._socket.recv(4096)
            allbuf += buf
            logger.debug("len %d raw:%s|", len(buf), buf)

            if len(buf) < 4096:
                cont = False

        return allbuf
