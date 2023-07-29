from ib_insync import MarketOrder, LimitOrder, StopOrder, Forex, util
from collections import deque
from datetime import timedelta
from strategy import Strategy
from constants import BALANCE, RISK, LOT_PRICE
import pandas as pd

buffer_bars = deque()
last_five_min_time = None


class Trader:
    def __init__(self, ib, contract):
        self.ib = ib
        self.contract = contract

    @staticmethod
    def define_contract(symbol):
        """Define a contract"""
        contract = Forex(symbol)
        return contract

    @staticmethod
    def connect_ib(ib):
        """Connect to IB"""
        ib.connect('127.0.0.1', 7497, clientId=1)

    def on_bar_update(self, df, bars, has_new_bar):
        """
        Esta función se ejecuta cada vez que se recibe una nueva barra de datos en tiempo real.

        Args:
            bars (List[BarData]): Lista de objetos BarData que representa las barras de datos en tiempo real recibidas hasta el momento.
            has_new_bar (bool): Un indicador booleano que señala si la última actualización incluye una nueva barra. Si es True, la última barra en 'bars' es una nueva barra. Si es False, la última barra en 'bars' se ha actualizado con nuevos datos.

        Dentro de la función, se comprueba si se ha recibido una nueva barra. Si es así, se extrae la última barra (la nueva barra) de 'bars'. Esta nueva barra se puede utilizar para realizar cálculos adicionales, generar señales de trading, o cualquier otra tarea que necesites.
        """
        global buffer_bars, last_five_min_time
        if has_new_bar:
            new_bar = bars[-1]
            # Convertir el nuevo bar en un DataFrame y añadirlo al buffer
            new_df = util.df([new_bar])
            buffer_bars.append(new_df)

            # Si han pasado más de 5 minutos desde el último bar de 5 minutos, creamos un nuevo bar de 5 minutos
            if (last_five_min_time is None or new_bar.date > last_five_min_time + timedelta(minutes=5)):
                # Crear una nueva vela de 5 minutos a partir del buffer y añadirla al DataFrame
                five_min_df = pd.concat(list(buffer_bars))
                five_min_df = five_min_df.resample('5Min').agg({'open': 'first',
                                                                'high': 'max',
                                                                'low': 'min',
                                                                'close': 'last',
                                                                'volume': 'sum'})
                df = pd.concat([df, five_min_df])

                # Limpiar el buffer y actualizar la última hora de la vela de 5 minutos
                buffer_bars.clear()
                last_five_min_time = new_bar.date

                # Llamar a la estrategia en el nuevo DataFrame
                action, stop_loss, take_profit = Strategy()(df)
                order = self._evaluate_action(action, stop_loss, take_profit)

                if order is not None:
                    self._execute_order(self.ib, order, self.contract)

    def _evaluate_action(self, action, stop_loss, take_profit):
        if action is not 'None':

            # Calcular el tamaño de la posición en lotes
            stop_loss_distance = abs(
                df['close'][-1] - stop_loss)  # type: ignore
            position_size_in_lots = BALANCE * RISK / \
                (stop_loss_distance * LOT_PRICE)

            # Crear una orden de stop loss y take profit
            order = self._create_order(
                action, position_size_in_lots, stop_loss, take_profit)

            return order
        return None

    def _create_order(self, action, totalQuantity, stop_loss, take_profit):
        """
        Esta función crea una orden de stop limit para stop loss y una orden limitada para take profit.

        Parámetros:
        - action (str): "BUY" o "SELL", dependiendo de si quieres comprar o vender.
        - totalQuantity (int): la cantidad total que quieres comprar o vender.
        - stop_loss (float): el precio al que quieres vender en caso de que el precio vaya en tu contra.
        - take_profit (float): el precio al que quieres vender en caso de que el precio vaya a tu favor.

        Retorna:
        - bracket_order: una lista de las dos órdenes que componen la orden de soporte (parent, take_profit, stop_loss)
        """

        # Si la acción es comprar, queremos vender para el stop loss y take profit, y viceversa
        opposite_action = "SELL" if action == "BUY" else "BUY"

        # Orden principal (a mercado)
        parent_order = MarketOrder(action, totalQuantity)

        # Orden de Stop Loss (Stop Limit Order)
        stop_order = StopOrder(opposite_action, totalQuantity,
                               stop_loss, parentId=parent_order.orderId, tif='GTC')

        # Orden de Take Profit (Limit Order)
        profit_order = LimitOrder(opposite_action, totalQuantity,
                                  take_profit, parentId=parent_order.orderId, tif='GTC')

        # Retornamos las ordenes en un bracket
        bracket_order = [parent_order, stop_order, profit_order]

        return bracket_order

    def _execute_order(ib, order, contract):
        # Por cada orden en la orden bracket, la colocamos
        for o in order:
            ib.placeOrder(contract, o)
            print(f'{o.action} {o.orderType} order submitted.')
