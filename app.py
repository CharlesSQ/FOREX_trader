from ib_insync import IB
from trader import Trader
from utils import check_time

# Crear una instancia de IB()
ib = IB()


def main():
    # Iniciar conexión con Interactive Brokers
    Trader.connect_ib(ib)

    # Definir el contrato (en este caso, la divisa que queremos operar: EURUSD)
    contract = Trader.define_contract('EURUSD')

    # Solicitar datos históricos de precios para el contrato desde el broker.
    # Estamos solicitando datos de los último día en barras de 5 minutos.
    # Los datos se muestran como el punto medio (MIDPOINT) entre el precio más alto y más bajo.
    print('Requesting historical data...')
    historique_bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='7200 S',
        barSizeSetting='1 min',
        whatToShow='MIDPOINT',
        useRTH=True,
        formatDate=1)

    # Crear una instancia de la clase Trader
    trader = Trader(ib, contract, historique_bars)

    # Suscribir a market data para obtener el spread
    trader.subscribe_ticker()

    # Suscribirse a las actualizaciones de datos en tiempo real
    bars = ib.reqRealTimeBars(contract, 5, 'MIDPOINT', False)
    bars.updateEvent += trader.on_bar_update

    # Iniciar la verificación de tiempo para detener el programa los sábados a las 00:00
    check_time(ib.disconnect)

    try:
        # Iniciar el ciclo de eventos del cliente de Interactive Brokers.
        # Esto mantendrá el programa en funcionamiento y procesará cualquier evento que venga del broker.
        ib.run()
    except (KeyboardInterrupt, Exception):
        # Cancelar la suscripción cuando se presiona Ctrl+C
        print('Cancelling subscription...')
        print('Ordenes agregadas', len(trader.all_orders))

        # Get orders from ib
        executed_orders = ib.fills()

        winning_orders = [
            order for order in executed_orders if order.profitLoss > 0]
        losing_orders = [
            order for order in executed_orders if order.profitLoss < 0]

        print("Ordenes ejecutadas: ", len(executed_orders))
        print("Ordenes ganadas: ", len(winning_orders))
        print("Ordenes perdidas: ", len(losing_orders))

        ib.cancelRealTimeBars(bars)

        if trader.ticker:
            ib.cancelMktData(trader.ticker)


if __name__ == "__main__":
    main()
