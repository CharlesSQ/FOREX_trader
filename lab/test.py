import sys
sys.path.append('/home/charles/Desktop/FOREX_trader')  # noqa

from strategies.utils import reset_buy_sell_flags, plot_bars_Bollinger_RSI
from typing import List
from dataclasses import dataclass
# from strategies.bollinger_RSI import Strategy
from strategies.bollinger_RSI_v2 import Strategy
from ib_insync import IB, util, Forex


@dataclass
class Order:
    action: str
    price_close: float
    stop_loss: float
    take_profit: float
    order_id: int


INITIAL_BALANCE: int = 500
RISK: float = 0.04
current_balance = INITIAL_BALANCE
all_orders: List[Order] = []
finished_orders = []


def create_order(action, price_close, stop_loss, take_profit, order_id):
    # print('create_order')

    # Orden principal (a mercado)
    order_object: Order = Order(
        action, price_close, stop_loss, take_profit, order_id)

    # Add order to current orders
    all_orders.append(order_object)


def evaluate_order(order: Order, higher_price, lower_price):
    global finished_orders

    # print('higher_price', higher_price)
    # print('lower_price', lower_price)
    # print('close', close)

    if order.action == 'SELL':
        if higher_price >= order.stop_loss:
            print('\n------------------------')
            print('action', order.action)
            print('price_close', order.price_close)
            # print('higher_price', higher_price)
            # print('lower_price', lower_price)
            print('LOSS')
            # print('higher_price', higher_price)
            # print('stop_loss', order.stop_loss)
            finished_orders.append(
                {'order_id': order.order_id, 'result': 'LOSS'})
            return 'LOSS'

        elif lower_price <= order.take_profit:
            print('\n------------------------')
            print('action', order.action)
            print('price_close', order.price_close)
            # print('higher_price', higher_price)
            # print('lower_price', lower_price)
            print('WIN')
            # print('lower_price', lower_price)
            # print('take_profit', order.take_profit)
            finished_orders.append(
                {'order_id': order.order_id, 'result': 'PROFIT'})
            return 'WIN'
        else:
            return 'None'

    elif order.action == 'BUY':
        if lower_price <= order.stop_loss:
            print('\n------------------------')
            print('action', order.action)
            print('price_close', order.price_close)
            # print('higher_price', higher_price)
            # print('lower_price', lower_price)
            print('LOSS')
            # print('lower_price', lower_price)
            # print('stop_loss', order.stop_loss)
            finished_orders.append(
                {'order_id': order.order_id, 'result': 'LOSS'})
            return 'LOSS'

        elif higher_price >= order.take_profit:
            print('\n------------------------')
            print('action', order.action)
            print('price_close', order.price_close)
            # print('higher_price', higher_price)
            # print('lower_price', lower_price)
            print('WIN')
            # print('higher_price', higher_price)
            # print('take_profit', order.take_profit)
            finished_orders.append(
                {'order_id': order.order_id, 'result': 'PROFIT'})
            return 'WIN'
        else:
            return 'None'


# Crear una instancia de IB()
ib = IB()
print('Conectando a IB')
ib.connect('localhost', 4002, clientId=5)

# 2. Definir el contrato (en este caso, la divisa que queremos operar: EURUSD)
contract = Forex('EURUSD')


def main():

    # 3. Solicitar datos históricos de precios para el contrato desde el broker.
    #    Estamos solicitando datos de los últimos 30 días en barras de 5 minutos.
    #    Los datos se muestran como el punto medio (MIDPOINT) entre el precio más alto y más bajo.
    print('Solicitando datos históricos')
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='20221014 23:59:00 US/Eastern',
        durationStr='5 D',
        barSizeSetting='5 mins',
        whatToShow='MIDPOINT',
        useRTH=True,
        formatDate=1)

    # 4. Convertir los datos obtenidos en un DataFrame de pandas para un manejo más fácil.
    df = util.df(bars)

    reset_buy_sell_flags()

    strategy = Strategy(test=True)
    run_strategy = True

    # Imprimir gráfico
    if df is not None:
        df_length = len(df)
        # Recorre cada fila del dataframe
        for i in range(df_length):
            # Solo evalúa la estrategia después de las primeras 40 barras (necesarios para calcular las Bandas de Bollinger)
            BARS_FOR_BOLLINGER = 100
            if i >= BARS_FOR_BOLLINGER:
                if run_strategy:
                    action, stop_loss, take_profit, price_close = strategy.run(
                        df.iloc[i-100:i+1], test=True)

                    if action != 'None':
                        create_order(
                            action, price_close, stop_loss, take_profit, i)
                        run_strategy = False

                else:
                    # Evaluate last order
                    order = all_orders[-1]
                    higher_price = df['high'].iloc[i]
                    lower_price = df['low'].iloc[i]
                    result = evaluate_order(order, higher_price, lower_price)
                    if result != 'None':
                        run_strategy = True

    # # Graficar en el plot.
    # df_copy = df.copy()

    # plot_bars_Bollinger_RSI(
    #     df_copy, strategy.buy_signals, strategy.sell_signals)

    # print('all_orders', all_orders)
    print('total orders', len(all_orders))
    # print('finished_orders', finished_orders)

    # Calculate number of wins and losses
    wins = 0
    losses = 0
    for order in finished_orders:
        if order['result'] == 'PROFIT':
            wins += 1
        elif order['result'] == 'LOSS':
            losses += 1
    # Calculate win rate
    win_rate = wins / (wins + losses) * 100

    print('wins', wins)
    print('losses', losses)
    print('win_rate', win_rate)


if __name__ == "__main__":
    main()
