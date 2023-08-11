from ib_insync import IB, util
from strategy import Strategy
from talib import BBANDS, RSI  # type: ignore
from trader import Trader
from dataclasses import dataclass
from typing import List
from utils import plot_bars_indicators


@dataclass
class Order:
    action: str
    totalQuantity: int
    stop_loss: float
    take_profit: float
    order_id: int


current_orders: List[Order] = []
finished_orders = []
balance = 10000


def create_order(action, totalQuantity, stop_loss, take_profit):
    print('create_order')

    # Orden principal (a mercado)
    current_orders_length = len(current_orders)
    print('current_orders_length', current_orders_length)
    order_object: Order = Order(
        action, totalQuantity, stop_loss, take_profit, current_orders_length)

    # Add order to current orders
    current_orders.append(order_object)


def evaluate_orders(df, i):
    print('evaluate_orders')
    # Recorre cada orden
    higher_price = df['high'][i]
    print('higher_price', higher_price)
    lower_price = df['low'][i]
    print('lower_price', lower_price)

    for order in current_orders:
        if order.action == 'SELL':
            if higher_price >= order.stop_loss:
                print('STOP LOSS')
                finished_orders.append(
                    {'order_id': order.order_id, 'result': 'LOSS'})
            elif lower_price <= order.take_profit:
                print('TAKE PROFIT')
                finished_orders.append(
                    {'order_id': order.order_id, 'result': 'PROFIT'})
        elif order.action == 'BUY':
            if lower_price <= order.stop_loss:
                print('STOP LOSS')
                finished_orders.append(
                    {'order_id': order.order_id, 'result': 'LOSS'})
            elif higher_price >= order.take_profit:
                print('TAKE PROFIT')
                finished_orders.append(
                    {'order_id': order.order_id, 'result': 'PROFIT'})


# Crear una instancia de IB()
ib = IB()
print('Conectando a IB')
Trader.connect_ib(ib)

# 2. Definir el contrato (en este caso, la divisa que queremos operar: EURUSD)
contract = Trader.define_contract('EURUSD')


def main():

    # 3. Solicitar datos históricos de precios para el contrato desde el broker.
    #    Estamos solicitando datos de los últimos 30 días en barras de 5 minutos.
    #    Los datos se muestran como el punto medio (MIDPOINT) entre el precio más alto y más bajo.
    print('Solicitando datos históricos')
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='7 D',
        barSizeSetting='5 mins',
        whatToShow='MIDPOINT',
        useRTH=True,
        formatDate=1)

    # 4. Convertir los datos obtenidos en un DataFrame de pandas para un manejo más fácil.
    df = util.df(bars)

    # Calcular las Bandas de Bollinger.
    df['upper_band'], df['middle_band'], df['lower_band'] = BBANDS(
        df['close'], timeperiod=20)

    # Calcular el RSI.
    df['RSI'] = RSI(df['close'], timeperiod=14)

    strategy = Strategy()

    # Imprimir gráfico
    if df is not None:
        df_length = len(df)
        # Recorre cada fila del dataframe
        for i in range(30):
            print('i', i)
            # Iniciar si current_order es menor a 10
            if len(current_orders) < 10000:
                # Solo evalúa la estrategia después de las primeras 2 horas (necesarios para calcular las Bandas de Bollinger)
                if i >= 24:
                    action, stop_loss, take_profit = strategy.run(
                        df.iloc[:i+1])

                    # Si la estrategia determina que debemos comprar o vender, creamos la orden y la enviamos al broker.
                    if action != 'None':
                        # Crear una orden de stop loss y take profit
                        totalQuantity = balance * 0.01
                        create_order(
                            action, totalQuantity, stop_loss, take_profit)

                    # # Evaluar ordenes actuales
                    evaluate_orders(df, i)

    plot_bars_indicators(df, strategy.buy_signals, strategy.sell_signals)
    print('current_orders', current_orders)
    print('total orders', len(current_orders))
    # print('finished_orders', finished_orders)

    # Calculate number of wins and losses
    # wins = 0
    # losses = 0
    # for order in finished_orders:
    #     if order['result'] == 'PROFIT':
    #         wins += 1
    #     elif order['result'] == 'LOSS':
    #         losses += 1
    # # Calculate win rate
    # win_rate = wins / (wins + losses) * 100

    # print('total_orders', wins + losses)
    # print('wins', wins)
    # print('losses', losses)
    # print('win_rate', win_rate)


if __name__ == "__main__":
    main()
