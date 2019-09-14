import threading

from ibapi.contract import Contract
from flask import Flask, request
from flask_restful import Resource, Api

import logging

from iblight.lightclient import LightIBrokerClient

logger = logging.getLogger(__name__)

_ibroker_client = None


def get_ibroker_client():
    global _ibroker_client
    if _ibroker_client is None:
        _ibroker_client = LightIBrokerClient()
        _ibroker_client.connect('127.0.0.1', 4003, 0)
        # This is BLOCKING: should it be running in some other thread???

        def run_ibroker():
            _ibroker_client.run()  # starts sending back notifications from IBroker TWS

        ib_client_thread = threading.Thread(target=run_ibroker)
        ib_client_thread.start()

    return _ibroker_client


class IBrokerMarketDataType(Resource):

    def get(self, data_type_id: int):
        get_ibroker_client().req_market_data_type(data_type_id)  # 4 = switch to delayed frozen data if live is not available
        return {'status-code': 'OK'}


class IBrokerMarketData(Resource):

    def get(self, req_id: int):
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        contract.primaryExchange = 'NASDAQ'
        get_ibroker_client().req_market_data(req_id, contract, '', False, False)
        return {'status-code': 'OK'}


class IBrokerPortfolioPositions(Resource):

    def get(self):
        get_ibroker_client().req_positions()
        return {'status-code': 'OK'}


class IBrokerAccountSummary(Resource):

    def get(self, req_id: int, group_name: str, tags: str):
        get_ibroker_client().req_account_summary(req_id, group_name=group_name, tags=tags)
        return {'status-code': 'OK'}


def main():
    # TODO: REST requests to EClient

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(IBrokerMarketDataType, '/mkt-data-type/<int:data_type_id>')
    api.add_resource(IBrokerMarketData, '/mkt-data/<int:req_id>')
    api.add_resource(IBrokerPortfolioPositions, '/positions')
    api.add_resource(IBrokerAccountSummary, '/account-summary/<int:req_id>/<string:group_name>/<string:tags>')

    app.run(debug=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    main()
