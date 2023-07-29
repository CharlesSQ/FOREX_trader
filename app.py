from ib_insync import MarketOrder, LimitOrder, StopOrder, IB, Forex, util
from trader import Trader
import datetime

# Crear una instancia de IB()
ib = IB()

current_orders = 0


def main():
    if current_orders < 10:
        # 1. Iniciar conexión con Interactive Brokers
        Trader.connect_ib(ib)

        # 2. Definir el contrato (en este caso, la divisa que queremos operar: EURUSD)
        contract = Trader.define_contract('EURUSD')
        trader = Trader(ib, contract)

        # 3. Solicitar datos históricos de precios para el contrato desde el broker.
        #    Estamos solicitando datos de los últimos 30 días en barras de 5 minutos.
        #    Los datos se muestran como el punto medio (MIDPOINT) entre el precio más alto y más bajo.
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='5 mins',
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=1)

        # 4. Convertir los datos obtenidos en un DataFrame de pandas para un manejo más fácil.
        df = util.df(bars)

        # Suscribirse a las actualizaciones de datos en tiempo real
        bars = ib.reqRealTimeBars(contract, 5, 'MIDPOINT', False)
        bars.updateEvent += trader.on_bar_update

        start_time = datetime.datetime.now()
        try:
            while True:
                ib.sleep(0.1)  # Pausa para no sobrecargar el CPU
                current_time = datetime.datetime.now()
                elapsed_time = current_time - start_time
                if elapsed_time.total_seconds() >= 7*24*60*60 or current_time.weekday() == 5:  # 5 es Sábado
                    break
        except KeyboardInterrupt:
            # Cancelar la suscripción cuando se presiona Ctrl+C
            pass

        # Cancelar la suscripción cuando hayas terminado
        ib.cancelRealTimeBars(bars)

        # 7. Iniciar el ciclo de eventos del cliente de Interactive Brokers.
        #     Esto mantendrá el programa en funcionamiento y procesará cualquier evento que venga del broker.
        ib.run()


if __name__ == "__main__":
    main()
