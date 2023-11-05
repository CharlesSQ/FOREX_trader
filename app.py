from ib_insync import IB
from trader import Trader
from ib_manager import IBManager, stop_IB
from strategies.utils import reset_buy_sell_flags
import logging
import datetime
import sys
import time
import json
import os

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="[%(asctime)s]%(levelname)s:%(message)s")

# Crear una instancia de IB()
ib = IB()
contract = None
bars = None

# Cargar el OCA counter
oca_group_counter: int = 0

# Crear el archivo de estado si no existe
if not os.path.exists('data/state.json'):
    data = {'oca_group_counter': 0, '_sell': 'ON', '_buy': 'ON'}

    with open('data/state.json', 'w') as f:
        json.dump(data, f)


def main():
    try:
        logging.info('Iniciando...')
        now = datetime.datetime.now()

        # Verificar si es domingo y si la hora actual es anterior a las 5 de la tarde y 5 minutos
        if now.weekday() == 6 and now.hour < 21:
            # Reset buy and sell flags
            reset_buy_sell_flags()

            # Esperar hasta las 5 de la tarde y 5 minutos
            logging.info('Esperando hasta las 5 de la tarde y 5 minutos...')
            wait_time = (datetime.datetime(now.year, now.month,
                         now.day, 21, 5, 0) - now).total_seconds()
            time.sleep(wait_time)
        elif now.minute % 5 == 0:
            FIVE_MINUTES = 300
            wait_time = FIVE_MINUTES - now.second - now.microsecond / 1000000
            logging.info(f'Esperando {wait_time} segundos...')
            time.sleep(wait_time)
        elif now.minute % 5 != 0:
            wait_time = 300 - (now.minute % 5) * 60 - \
                now.second - now.microsecond / 1000000
            logging.info(f'Esperando {wait_time} segundos...')
            time.sleep(wait_time)
        else:
            pass

        # Iniciar conexión con Interactive Brokers
        ib_manager = IBManager(ib)
        ib_manager.connect_to_ib()

        # Definir el contrato (en este caso, la divisa que queremos operar: EURUSD)
        global contract
        contract = Trader.define_contract('EURUSD')
        ib_manager.contract = contract

        # Solicitar datos históricos de precios para el contrato desde el broker.
        # Estamos solicitando datos de los último día en barras de 5 minutos.
        # Los datos se muestran como el punto medio (MIDPOINT) entre el precio más alto y más bajo.
        logging.info('Requesting historical data...')
        historique_bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='30000 S',  # 500 minutos = 100 barras de 5 minutos
            barSizeSetting='5 mins',
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=1)

        # Crear una instancia de la clase Trader
        trader = Trader(ib, contract, historique_bars)

        # Suscribir a market data para obtener el spread
        # trader.subscribe_ticker()

        # Suscribirse a las actualizaciones de datos en tiempo real
        logging.info('Subscribing to real time bars...')
        global bars
        bars = ib.reqRealTimeBars(contract, 5, 'MIDPOINT', False)
        ib_manager.requestedBars = bars

        # Asignar el evento de actualización de barras a la función on_bar_update de la clase Trader
        bars.updateEvent += trader.on_bar_update

        # Asignar el evento de error de IB a la función handle_ib_error de la clase IBManager
        ib.disconnectedEvent += ib_manager.handle_ib_disconnected

        # Iniciar el ciclo de eventos del cliente de Interactive Brokers.
        logging.info('Inicio del ciclo de eventos del cliente de IB...')
        ib.run()
    except Exception as e:
        raise e


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(f'Error desconocido: {e}')
            stop_IB(ib, bars, contract)
            logging.info('Reintentando la conexión en 5 segundos...')
            time.sleep(5)
