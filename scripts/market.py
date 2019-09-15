import json
import logging
import threading

from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse

from iblight.lightclient import LightIBrokerClient
from iblight.model import Contract
from iblight.model.schema import ContractSchema

logger = logging.getLogger(__name__)

_ibroker_client = None

_host, _port, _client_id = None, None, None


def set_ibroker_params(host: str, port: int, client_id: int):
    global _host
    global _port
    global _client_id
    _host, _port, _client_id = host, port, client_id


def get_ibroker_client():
    global _ibroker_client
    global _host
    global _port
    global _client_id
    if _ibroker_client is None:
        if None in (_host, _port, _client_id):
            raise ConnectionRefusedError('Programming error: IBroker connection not initialized'
                                         + ' - needs to set all parameters with '
                                         + 'set_ibroker_params(host: str, port: int, client_id: int)')

        _ibroker_client = LightIBrokerClient(_host, _port, _client_id)
        _ibroker_client.connect()

        # This is BLOCKING: should it be running in some other thread???

        def run_ibroker():
            _ibroker_client.run()  # starts sending back notifications from IBroker TWS

        ib_client_thread = threading.Thread(target=run_ibroker)
        ib_client_thread.start()

    return _ibroker_client


class IBrokerMarketDataType(Resource):

    def get(self, data_type_id: int):
        get_ibroker_client().req_market_data_type(
            data_type_id)  # 4 = switch to delayed frozen data if live is not available
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


class IBrokerContract(Resource):

    def post(self):
        json_data = request.get_json(force=True)
        posted_contract = ContractSchema().load(json_data['contract'])
        get_ibroker_client().req_contract_details(req_id=json_data['req_id'], contract=posted_contract)
        return {'status-code': 'OK'}


class IBrokerContractSmartStockUS(Resource):

    def get(self, req_id: int, symbol: str):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.currency = "USD"
        contract.exchange = "SMART"
        get_ibroker_client().req_contract_details(req_id, contract=contract)
        return {'status-code': 'OK'}


def main():
    # TODO: REST requests to EClient

    set_ibroker_params('127.0.0.1', 4003, 0)
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(IBrokerMarketDataType, '/mkt-data-type/<int:data_type_id>')
    api.add_resource(IBrokerMarketData, '/mkt-data/<int:req_id>')
    api.add_resource(IBrokerPortfolioPositions, '/positions')
    api.add_resource(IBrokerAccountSummary, '/account-summary/<int:req_id>/<string:group_name>/<string:tags>')
    api.add_resource(IBrokerContract, '/contract')
    api.add_resource(IBrokerContractSmartStockUS, '/contract/<int:req_id>/<string:symbol>')

    app.run(debug=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    main()
