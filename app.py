from ib_insync import IB
from trader import Trader
from utils import check_time
import datetime

# Crear una instancia de IB()
ib = IB()

current_orders = 0
start_time = datetime.datetime.now()


def main():
    if current_orders < 10:
        # Iniciar conexión con Interactive Brokers
        Trader.connect_ib(ib)

        # Definir el contrato (en este caso, la divisa que queremos operar: EURUSD)
        contract = Trader.define_contract('EURUSD')

        # Solicitar datos históricos de precios para el contrato desde el broker.
        # Estamos solicitando datos de los último día en barras de 5 minutos.
        # Los datos se muestran como el punto medio (MIDPOINT) entre el precio más alto y más bajo.
        historique_bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='5 mins',
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=1)

        # Crear una instancia de la clase Trader
        trader = Trader(ib, contract, historique_bars)

        # Suscribirse a las actualizaciones de datos en tiempo real
        bars = ib.reqRealTimeBars(contract, 5, 'MIDPOINT', False)
        bars.updateEvent += trader.on_bar_update

        # Iniciar la verificación de tiempo para detener el programa los sábados a las 00:00
        check_time(ib.disconnect)

        try:
            # Iniciar el ciclo de eventos del cliente de Interactive Brokers.
            # Esto mantendrá el programa en funcionamiento y procesará cualquier evento que venga del broker.
            ib.run()
        except KeyboardInterrupt:
            # Cancelar la suscripción cuando se presiona Ctrl+C
            ib.cancelRealTimeBars(bars)


if __name__ == "__main__":
    main()
