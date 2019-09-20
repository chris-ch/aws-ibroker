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

_ibroker_gateway = None


def connect_ibroker_gateway(host: str, port: int, client_id: int):
    if None in (host, port, client_id):
        raise ConnectionRefusedError('Programming error: IBroker connection not initialized'
                                     + ' - needs to set all parameters with '
                                     + 'set_ibroker_params(host: str, port: int, client_id: int)')

    ibroker_client = LightIBrokerClient(host, port, client_id)
    ibroker_client.connect()

    # This is BLOCKING: should it be running in some other thread???

    def run_ibroker():
        ibroker_client.run()  # starts sending back notifications from IBroker TWS

    ib_client_thread = threading.Thread(target=run_ibroker)
    ib_client_thread.start()

    return ibroker_client


def market_data_start_handler(ibroker_gateway: LightIBrokerClient):
    def market_data_start(req_id: int):
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.sec_type = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        contract.primary_exchange = 'NASDAQ'
        ibroker_gateway.req_market_data(req_id, contract, '', False, False)
        return {'status-code': 'OK'}

    return market_data_start


def market_data_stop_handler(ibroker_gateway: LightIBrokerClient):
    def market_data_stop(req_id: int):
        ibroker_gateway.cancel_market_data(req_id)
        return {'status-code': 'OK'}

    return market_data_stop


def portfolio_positions_handler(ibroker_gateway: LightIBrokerClient):
    def portfolio_positions():
        ibroker_gateway.req_positions()
        return {'status-code': 'OK'}

    return portfolio_positions


def market_data_type_handler(ibroker_gateway: LightIBrokerClient):
    def market_data_type(data_type_id: int):
        ibroker_gateway.req_market_data_type(data_type_id)  # 4 = switch to delayed frozen data if live is not available
        return {'status-code': 'OK'}

    return market_data_type


def account_start_handler(ibroker_gateway: LightIBrokerClient):
    def account_start(req_id: int, group_name: str, tags: str):
        """
        Starts sending account summary notifications.
        @param req_id request id
        @param group_name the group name, such as "All"
        @param tags the fields, such as "NetLiquidation"
        @return a status
        """
        ibroker_gateway.req_account_summary(req_id=req_id, group_name=group_name, tags=tags)
        return {'status-code': 'OK'}

    return account_start


def account_stop_handler(ibroker_gateway: LightIBrokerClient):
    def account_stop(req_id: int):
        """
        Stops sending account summary notifications.
        @param req_id request id
        :param req_id:
        :return:
        """
        ibroker_gateway.cancel_account_summary(req_id)
        return {'status-code': 'OK'}

    return account_stop


def load_contract_details_handler(ibroker_gateway: LightIBrokerClient):
    def load_contract_details(req_id: int, contract: dict):
        contract_model = ContractSchema().load(contract)
        ibroker_gateway.req_contract_details(req_id=req_id, contract=contract_model)
        return {'status-code': 'OK'}

    return load_contract_details


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    global _ibroker_gateway
    if not _ibroker_gateway:
        _ibroker_gateway = connect_ibroker_gateway('127.0.0.1', 4003, 0)

    dispatcher["account-start"] = account_start_handler(_ibroker_gateway)
    dispatcher["account-stop"] = account_stop_handler(_ibroker_gateway)
    dispatcher["market-data-type"] = market_data_type_handler(_ibroker_gateway)
    dispatcher["market-data-start"] = market_data_start_handler(_ibroker_gateway)
    dispatcher["market-data-stop"] = market_data_stop_handler(_ibroker_gateway)
    dispatcher["portfolio-positions"] = portfolio_positions_handler(_ibroker_gateway)
    dispatcher["load-contract-details"] = load_contract_details_handler(_ibroker_gateway)
    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


def main():
    run_simple('localhost', 8000, application)
    logging.info("listening to http://127.0.0.1:8000")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    main()
