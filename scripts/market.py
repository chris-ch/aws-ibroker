from ibapi.contract import Contract

import logging

from iblight.lightclient import LightIBrokerClient

logger = logging.getLogger(__name__)


def main():
    # TODO: REST requests to EClient
    app = LightIBrokerClient()
    app.connect('127.0.0.1', 4003, 0)
    contract = Contract()
    contract.symbol = 'AAPL'
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.primaryExchange = 'NASDAQ'
    app.reqMarketDataType(4)  # Switch to delayed forzen data if live is not available
    app.reqMktData(1, contract, '', False, False)
    app.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    main()
