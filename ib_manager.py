from ib_insync import IB, RealTimeBarList, Contract
import logging
import sys
import asyncio

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="[%(asctime)s]%(levelname)s:%(message)s")


class IBManager:

    def __init__(self, ib_instance: IB):
        self.ib = ib_instance
        self._ibConnected = False
        self._requestedBars: RealTimeBarList = None
        self._contract: Contract = None

    def connect_to_ib(self):
        self.ib.disconnect()  # Desconectar primero

        while True:
            try:
                if self._ibConnected:
                    logging.info('Ya está conectado.')
                    return
                else:
                    logging.info('Intentando conectar a IB...')
                    self.ib.connect('ib-gateway-service', 4002, clientId=999)
                    # self.ib.connect('localhost', 4002, clientId=2)
                    if self.ib.isConnected():
                        self._ibConnected = True
                        logging.info('Conexión establecida.')
                        return

            except Exception as e:
                logging.info('\n')
                logging.info(
                    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
                logging.info(f'Error al conectar: {e}')
                logging.info(
                    'Esperando 10 segundos antes de intentar de nuevo...')
                IB.sleep(5)

    def handle_ib_disconnected(self):
        logging.error("Conexión perdida: Peer closed connection")
        try:
            stop_IB(self.ib, self._requestedBars, self._contract)
        except Exception as e:
            raise e

    @property
    def requestedBars(self):
        return self._requestedBars

    @requestedBars.setter
    def requestedBars(self, value):
        self._requestedBars = value

    @property
    def contract(self):
        return self._contract

    @contract.setter
    def contract(self, value):
        self._contract = value


def stop_IB(ib_instance: IB, requestedBars: RealTimeBarList, contract: Contract):
    try:
        logging.info('Deteniendo operaciones antes de reiniciar...')

        # cancel_subscriptions(ib_instance, requestedBars, contract)

        ib_instance.disconnect()
        logging.info('Desconectado')

        # Reiniciar la instancia de IB
        logging.info('Reiniciando instancia de IB...')
        global ib
        ib = None
        ib = IB()

        logging.info('Cancelando tareas...')
        for task in asyncio.all_tasks():
            task.cancel()

        logging.info('Deteniendo loop...')
        loop = asyncio.get_running_loop()

        # Verificar primero si el loop ya está detenido
        if not loop.is_closed():
            loop.stop()
            logging.info('Loop detenido')
    except Exception as e:
        raise e


def cancel_subscriptions(ib_instance: IB, requestedBars: RealTimeBarList, contract: Contract):
    try:
        logging.info('Cancelando suscripciones...')
        ib_instance.cancelRealTimeBars(requestedBars)
        ib_instance.cancelMktData(contract)
    except Exception as e:
        raise e
