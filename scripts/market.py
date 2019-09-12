from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        print('Error', reqId)

    def tickPrice(self, reqId, tickType, price, attrib):
        print('Tick price', reqId, tickType, price)

    def tickSize(self, reqId, tickType, size):
        print('Tick size', reqId, tickType, size)


def main():
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
    main()
