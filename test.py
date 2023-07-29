from ib_insync import IB, util
from strategy import Strategy
from broker_api import connect_ib, define_contract
from dataclasses import dataclass
from typing import List
import plotly.graph_objects as go


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
    order_object: Order = Order(
        action, totalQuantity, stop_loss, take_profit, current_orders_length)

    # Add order to current orders
    current_orders.append(order_object)


def evaluate_orders(dfi):
    print('evaluate_orders')
    # Recorre cada orden
    higher_price = dfi['High']
    print('higher_price', higher_price)
    lower_price = dfi['Low']
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
connect_ib(ib)

# 2. Definir el contrato (en este caso, la divisa que queremos operar: EURUSD)
contract = define_contract('EURUSD')


def main():

    def on_bar_update(bars, has_new_bar):
        print('on_bar_update')
        if has_new_bar:
            new_bar = bars[-1]
            print(round(new_bar.close, 2))

    # Primero, debes suscribirte a las actualizaciones de datos en tiempo real.
    print('Solicitando datos en tiempo real')
    bars = ib.reqRealTimeBars(contract, 5, 'MIDPOINT', False)
    bars.updateEvent += on_bar_update

    # Recoge datos durante 30 segundos. Puedes cambiar esto según tus necesidades.
    print('Recogiendo datos durante 30 segundos')
    ib.sleep(30)

    # No olvides cancelar la suscripción cuando hayas terminado.
    print('Cancelando suscripción')
    ib.cancelRealTimeBars(bars)

    # # 3. Solicitar datos históricos de precios para el contrato desde el broker.
    # #    Estamos solicitando datos de los últimos 30 días en barras de 5 minutos.
    # #    Los datos se muestran como el punto medio (MIDPOINT) entre el precio más alto y más bajo.
    # print('Solicitando datos históricos')
    # bars = ib.reqHistoricalData(
    #     contract,
    #     endDateTime='',
    #     durationStr='1 D',
    #     barSizeSetting='5 mins',
    #     whatToShow='MIDPOINT',
    #     useRTH=True,
    #     formatDate=1)

    # # 4. Convertir los datos obtenidos en un DataFrame de pandas para un manejo más fácil.
    # df = util.df(bars)

    # fig = go.Figure(data=[go.Candlestick(x=df.index,
    #                                      open=df['open'],
    #                                      high=df['high'],
    #                                      low=df['low'],
    #                                      close=df['close'])])
    # fig.show()

    # if df is not None:
    #     df_length = len(df)
    #     # Recorre cada fila del dataframe
    #     for i in range(df_length):
    #         # Iniciar si current_order es menor a 10
    #         if len(current_orders) < 10:
    #             # Solo evalúa la estrategia después de los primeros 20 días (necesarios para calcular las Bandas de Bollinger)
    #             if i >= 20:
    #                 action, stop_loss, take_profit = Strategy()(df.iloc[:i+1])
    #                 print('action', action)

    #                 # Si la estrategia determina que debemos comprar o vender, creamos la orden y la enviamos al broker.
    #                 if action is not 'None':
    #                     # Crear una orden de stop loss y take profit
    #                     totalQuantity = balance * 0.01
    #                     order = create_order(
    #                         action, totalQuantity, stop_loss, take_profit)

    #                 # Evaluar ordenes actuales
    #                 evaluate_orders(df.iloc[i])

    # print('current_orders', current_orders)
    # print('finished_orders', finished_orders)

    # # Calculate number of wins and losses
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
