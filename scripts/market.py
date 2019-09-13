from ibapi.client import EClient, TickerId
from ibapi.utils import current_fn_name
from ibapi.contract import Contract
from ibapi.ticktype import TickType

import logging

from scripts.lightclient import LightIBrokerClient

logger = logging.getLogger(__name__)


class TestApp(LightIBrokerClient):

    def __init__(self):
        LightIBrokerClient.__init__(self, self)

    def logAnswer(self, fnName, fnParams):
        if logger.isEnabledFor(logging.INFO):
            if 'self' in fnParams:
                prms = dict(fnParams)
                del prms['self']
            else:
                prms = fnParams
            logger.info("ANSWER %s %s", fnName, prms)


    def error(self, reqId, errorCode, errorString):
        print('Error', reqId)

    def tickPrice(self, reqId, tickType, price, attrib):
        print('Tick price', reqId, tickType, price)

    def tickSize(self, reqId, tickType, size):
        print('Tick size', reqId, tickType, size)

    def connectAck(self):
        """ callback signifying completion of successful connection """
        self.logAnswer(current_fn_name(), vars())

    def connectionClosed(self):
        """This function is called when TWS closes the sockets
        connection with the ActiveX control, or when TWS is shut down."""

        self.logAnswer(current_fn_name(), vars())

    def managedAccounts(self, accountsList:str):
        """Receives a comma-separated string with the managed account ids."""
        self.logAnswer(current_fn_name(), vars())

    def nextValidId(self, orderId:int):
        """ Receives next valid order id."""

        self.logAnswer(current_fn_name(), vars())

    def tickReqParams(self, tickerId:int, minTick:float, bboExchange:str, snapshotPermissions:int):
        """returns exchange map of a particular contract"""
        self.logAnswer(current_fn_name(), vars())

    def marketDataType(self, reqId:TickerId, marketDataType:int):
        """TWS sends a marketDataType(type) callback to the API, where
        type is set to Frozen or RealTime, to announce that market data has been
        switched between frozen and real-time. This notification occurs only
        when market data switches between real-time and frozen. The
        marketDataType( ) callback accepts a reqId parameter and is sent per
        every subscription because different contracts can generally trade on a
        different schedule."""

        self.logAnswer(current_fn_name(), vars())

    def tickString(self, reqId:TickerId, tickType:TickType, value:str):
        self.logAnswer(current_fn_name(), vars())


def main():
    # TODO: REST requests to EClient
    app = TestApp()
    app.connect('127.0.0.1', 4003, 0)
    contract = Contract()
    contract.symbol = 'AAPL'
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.primaryExchange = 'NASDAQ'
    app.reqMarketDataType(4)  # Switch to delayed forzen data if live is not available
    app.reqMktData(1, contract, '', False, False, [])
    app.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    main()
