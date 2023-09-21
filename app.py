from ib_insync import IB
from trader import Trader
from ib_manager import IBManager
import logging
import sys
import asyncio
import time

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="[%(asctime)s]%(levelname)s:%(message)s")

# Crear una instancia de IB()
ib = IB()


def main():
    # Iniciar conexión con Interactive Brokers
    ib_manager = IBManager(ib)
    ib_manager.connect_to_ib()

    # Definir el contrato (en este caso, la divisa que queremos operar: EURUSD)
    contract = Trader.define_contract('EURUSD')
    ib_manager.contract = contract

    # Solicitar datos históricos de precios para el contrato desde el broker.
    # Estamos solicitando datos de los último día en barras de 5 minutos.
    # Los datos se muestran como el punto medio (MIDPOINT) entre el precio más alto y más bajo.
    logging.info('Requesting historical data...')
    historique_bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='9000 S',  # 150 minutos = 30 barras de 5 minutos
        barSizeSetting='5 mins',
        whatToShow='MIDPOINT',
        useRTH=True,
        formatDate=1)

    # Crear una instancia de la clase Trader
    trader = Trader(ib, contract, historique_bars)

    # Suscribir a market data para obtener el spread
    trader.subscribe_ticker()

    # Suscribirse a las actualizaciones de datos en tiempo real
    logging.info('Subscribing to real time bars...')
    bars = ib.reqRealTimeBars(contract, 5, 'MIDPOINT', False)
    ib_manager.requestedBars = bars

    # Asignar el evento de actualización de barras a la función on_bar_update de la clase Trader
    bars.updateEvent += trader.on_bar_update

    # Asignar el evento de error de IB a la función handle_ib_error de la clase IBManager
    ib.errorEvent += ib_manager.handle_ib_error

    # Iniciar el ciclo de eventos del cliente de Interactive Brokers.
    logging.info('Inicio del ciclo de eventos del cliente de IB...')
    ib.run()


if __name__ == "__main__":
    while True:
        try:
            main()
        except ConnectionError as e:
            logging.error(f'Error de conexión: {e}')
            logging.info('Reintentando la conexión en 5 segundos...')
            ib.disconnect()
            time.sleep(5)
        except Exception as e:
            logging.error(f'Error desconocido: {e}')
            ib.disconnect()
            sys.exit(1)
