from ib_insync import MarketOrder, LimitOrder, StopOrder, IB, Forex, util
from broker_api import define_contract, connect_ib, create_order
from strategy import Strategy

# Crear una instancia de IB()
ib = IB()

current_orders = 0
BALANCE = 10000
RISK = 0.01
LOT_PRICE = 10


def main():
    if current_orders < 10:
        # 1. Iniciar conexión con Interactive Brokers
        connect_ib(ib)

        # 2. Definir el contrato (en este caso, la divisa que queremos operar: EURUSD)
        contract = define_contract('EURUSD')

        # 3. Solicitar datos históricos de precios para el contrato desde el broker.
        #    Estamos solicitando datos de los últimos 30 días en barras de 5 minutos.
        #    Los datos se muestran como el punto medio (MIDPOINT) entre el precio más alto y más bajo.
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='30 D',
            barSizeSetting='5 mins',
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=1)

        # 4. Convertir los datos obtenidos en un DataFrame de pandas para un manejo más fácil.
        df = util.df(bars)

        # 5. Obtener la señal de trading de la estrategia.
        action, stop_loss, take_profit = Strategy()(df)

        print('action', action)

        # 6. Si la estrategia determina que debemos comprar o vender, creamos la orden y la enviamos al broker.
        if action is not 'None':

            # Calcular el tamaño de la posición en lotes
            stop_loss_distance = abs(
                df['close'][-1] - stop_loss)  # type: ignore
            position_size_in_lots = BALANCE * RISK / \
                (stop_loss_distance * LOT_PRICE)

            # Crear una orden de stop loss y take profit
            order = create_order(
                action, position_size_in_lots, stop_loss, take_profit)

            # Por cada orden en la orden bracket, la colocamos
            for o in order:
                ib.placeOrder(contract, o)
                print(f'{o.action} {o.orderType} order submitted.')

        # 7. Iniciar el ciclo de eventos del cliente de Interactive Brokers.
        #     Esto mantendrá el programa en funcionamiento y procesará cualquier evento que venga del broker.
        ib.run()


if __name__ == "__main__":
    main()
