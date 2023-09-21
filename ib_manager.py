from ib_insync import IB, RealTimeBarList, Contract
import logging
import sys
import time

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="[%(asctime)s]%(levelname)s:%(message)s")


class IBManager:

    def __init__(self, ib_instance: IB):
        self.ib = ib_instance
        self._ibConnected = False
        self._requestedBars: RealTimeBarList = None
        self._contract: Contract = None

    def handle_ib_error(self, reqId, errorCode, errorString, contract):
        logging.error(f"Conexión perdida: {errorString}")
        if errorCode == 1100:
            self._ibConnected = False
            self.cancel_subscriptions()
            raise ConnectionError("Error de conexión con IB")

    def cancel_subscriptions(self):
        self.ib.cancelRealTimeBars(self._requestedBars)
        self.ib.cancelMktData(self._contract)

    def connect_to_ib(self):
        self.ib.disconnect()  # Desconectar primero

        while True:
            try:
                if self._ibConnected:
                    logging.info('Ya está conectado.')
                    return
                else:
                    logging.info('Intentando conectar a IB...')
                    # ib.connect('ib_gateway', 4002, clientId=999)
                    self.ib.connectAsync('localhost', 4002, clientId=2)
                    if self.ib.isConnected():
                        self._ibConnected = True
                        logging.info('Conexión establecida.')
                        return

            except Exception as e:
                logging.info(f'Error al conectar: {e}')
                logging.info(
                    'Esperando 60 segundos antes de intentar de nuevo...')
                time.sleep(6)  # Espera 60 segundos antes de intentar de nuevo.

    @property
    def requestedBars(self):
        return self._requestedBars

    @requestedBars.setter
    def set_requestedBars(self, value):
        self._requestedBars = value

    @property
    def contract(self):
        return self._contract

    @contract.setter
    def set_contract(self, value):
        self._contract = value
