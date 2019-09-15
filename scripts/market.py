import json
import logging
import threading

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher

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


def market_data_start(req_id: int):
    contract = Contract()
    contract.symbol = 'AAPL'
    contract.sec_type = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    contract.primary_exchange = 'NASDAQ'
    get_ibroker_client().req_market_data(req_id, contract, '', False, False)
    return {'status-code': 'OK'}


def market_data_stop(req_id: int):
    get_ibroker_client().cancel_market_data(req_id)
    return {'status-code': 'OK'}


def portfolio_positions():
    get_ibroker_client().req_positions()
    return {'status-code': 'OK'}


def market_data_type(data_type_id: int):
    get_ibroker_client().req_market_data_type(
        data_type_id)  # 4 = switch to delayed frozen data if live is not available
    return {'status-code': 'OK'}


def account_start(req_id: int, group_name: str, tags: str):
    """
    Starts sending account summary notifications.
    @param req_id request id
    @param group_name the group name, such as "All"
    @param tags the fields, such as "NetLiquidation"
    @return a status
    """
    get_ibroker_client().req_account_summary(req_id=req_id, group_name=group_name, tags=tags)
    return {'status-code': 'OK'}


def account_stop(req_id: int):
    """
    Stops sending account summary notifications.
    @param req_id request id
    :param req_id:
    :return:
    """
    get_ibroker_client().cancel_account_summary(req_id)
    return {'status-code': 'OK'}


def load_contract_details(req_id: int, contract: dict):
    contract_model = ContractSchema().load(contract)
    get_ibroker_client().req_contract_details(req_id=req_id, contract=contract_model)
    return {'status-code': 'OK'}


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["account-start"] = account_start
    dispatcher["account-stop"] = account_stop
    dispatcher["market-data-type"] = market_data_type
    dispatcher["market-data-start"] = market_data_start
    dispatcher["market-data-stop"] = market_data_stop
    dispatcher["portfolio-positions"] = portfolio_positions
    dispatcher["load-contract-details"] = load_contract_details
    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


def main():
    set_ibroker_params('127.0.0.1', 4003, 0)

    logging.info("listening to http://127.0.0.1:8000")

    run_simple('localhost', 8000, application)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    main()
