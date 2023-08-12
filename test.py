from ib_insync import IB, util
from strategies.bollinger_RSI import Strategy
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


BALANCE = 10000
ORDERS_LIMIT = 10000
current_orders: List[Order] = []
finished_orders = []


def create_order(action, totalQuantity, stop_loss, take_profit, order_id):
    # print('create_order')

    # Orden principal (a mercado)
    order_object: Order = Order(
        action, totalQuantity, stop_loss, take_profit, order_id)

    # Add order to current orders
    current_orders.append(order_object)


def evaluate_orders(df):
    print('evaluate_orders')

    for order in current_orders:
        # Recorre cada orden
        df_length = len(df)

        # Recorrer cada fila del dataframe a partir de la fila en la que se creó la orden
        for i in range(order.order_id, df_length):
            # Recorre cada fila del dataframe
            higher_price = df['high'][i]
            lower_price = df['low'][i]

            if order.action == 'SELL':
                if higher_price >= order.stop_loss:
                    print('action', order.action)
                    print('higher_price', higher_price)
                    print('stop_loss', order.stop_loss)
                    finished_orders.append(
                        {'order_id': order.order_id, 'result': 'LOSS'})
                    break

                elif lower_price <= order.take_profit:
                    print('action', order.action)
                    print('lower_price', lower_price)
                    print('take_profit', order.take_profit)
                    finished_orders.append(
                        {'order_id': order.order_id, 'result': 'PROFIT'})
                    break

            elif order.action == 'BUY':
                if lower_price <= order.stop_loss:
                    print('action', order.action)
                    print('lower_price', lower_price)
                    print('stop_loss', order.stop_loss)
                    finished_orders.append(
                        {'order_id': order.order_id, 'result': 'LOSS'})
                    break

                elif higher_price >= order.take_profit:
                    print('action', order.action)
                    print('higher_price', higher_price)
                    print('take_profit', order.take_profit)
                    finished_orders.append(
                        {'order_id': order.order_id, 'result': 'PROFIT'})
                    break


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
        endDateTime='20230721 23:59:00 US/Eastern',
        durationStr='5 D',
        barSizeSetting='1 min',
        whatToShow='MIDPOINT',
        useRTH=True,
        formatDate=1)

    # 4. Convertir los datos obtenidos en un DataFrame de pandas para un manejo más fácil.
    df = util.df(bars)

    strategy = Strategy()

    # Imprimir gráfico
    if df is not None:
        df_length = len(df)
        # Recorre cada fila del dataframe
        for i in range(df_length):
            # Iniciar si current_order es menor a 10
            if len(current_orders) < ORDERS_LIMIT:
                # Solo evalúa la estrategia después de las primeras 40 barras (necesarios para calcular las Bandas de Bollinger)
                if i >= 40:
                    action, stop_loss, take_profit = strategy.run(
                        df.iloc[:i+1])

                    # Si la estrategia determina que debemos comprar o vender, creamos la orden y la enviamos al broker.
                    if action != 'None':
                        # print('i', i)
                        # Crear una orden de stop loss y take profit
                        totalQuantity = BALANCE * 0.01
                        create_order(
                            action, totalQuantity, stop_loss, take_profit, i)

    # Calcular las indicadores para graficarlas en el plot.
    df_copy = df.copy()

    df_copy['upper_band'], df_copy['middle_band'], df_copy['lower_band'] = BBANDS(
        df_copy['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df_copy['RSI'] = RSI(df_copy['close'], timeperiod=14)

    plot_bars_indicators(df_copy, strategy.buy_signals, strategy.sell_signals)

    # Evaluar ordenes actuales
    evaluate_orders(df)

    # print('current_orders', current_orders)
    print('total orders', len(current_orders))
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
