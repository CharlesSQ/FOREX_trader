from ib_insync import IB, BarData, Contract, MarketOrder, LimitOrder, StopOrder, Order, Forex, util
from typing import List, Optional
from collections import deque
from datetime import timedelta
from strategies.bollinger_RSI import Strategy
from constants import BALANCE, RISK, LOT_PRICE
from utils import plot_only_bars
import pandas as pd
import numpy as np
import array


class Trader:
    def __init__(self, ib: IB, contract: Contract, bars: List[BarData]):
        print('Initializing Trader...')
        self.ib = ib
        self.contract = contract
        self.df = util.df(bars)
        self.buffer_dfs = deque()
        self.last_five_min_time = None
        self.current_orders: int = 0

    @staticmethod
    def define_contract(symbol: str) -> Contract:
        """Define a contract"""
        print(f'Defining contract for {symbol}...')
        contract = Forex(symbol)
        return contract

    def connect_ib(ib: IB):
        """Connect to IB"""
        print('Connecting to Interactive Brokers...')
        ib.connect('127.0.0.1', 7497, clientId=1)

    def on_bar_update(self, bars: List[BarData], has_new_bar: bool):
        """
        Esta función se ejecuta cada vez que se recibe una nueva barra de datos en tiempo real.

        Args:
            bars (List[BarData]): Lista de objetos BarData que representa las barras de datos en tiempo real recibidas hasta el momento.
            has_new_bar (bool): Un indicador booleano que señala si la última actualización incluye una nueva barra. Si es True, la última barra en 'bars' es una nueva barra. Si es False, la última barra en 'bars' se ha actualizado con nuevos datos.

        Dentro de la función, se comprueba si se ha recibido una nueva barra. Si es así, se extrae la última barra (la nueva barra) de 'bars'. Esta nueva barra se puede utilizar para realizar cálculos adicionales, generar señales de trading, o cualquier otra tarea que necesites.
        """
        print('********** Updating bars **********')
        if has_new_bar:
            print('New bar received')
            new_bar = bars[-1]
            # Convertir el nuevo bar en un DataFrame y añadirlo al buffer
            new_df = util.df([new_bar])
            print('new_df columns', new_df.columns)
            self.buffer_dfs.append(new_df)
            print('New bar added to buffer')
            print(f'buffer size: {len(self.buffer_dfs)}')

            # Si han pasado más de 5 minutos desde el último bar de 5 minutos, creamos un nuevo bar de 5 minutos
            if (self.last_five_min_time is None or new_bar.time > self.last_five_min_time + timedelta(minutes=1)):
                print('"""Creating new 5 minute bar..."""')
                # Crear una nueva vela de 5 minutos a partir del buffer y añadirla al DataFrame
                five_min_df = pd.concat(self.buffer_dfs)
                five_min_df.set_index('time', inplace=True)
                print('df columns', self.df.columns)
                five_min_df = five_min_df.resample('1Min').agg({'open_': 'first',
                                                                'high': 'max',
                                                                'low': 'min',
                                                                'close': 'last',
                                                                'volume': 'sum'})

                five_min_df = five_min_df.rename(columns={'open_': 'open'})

                columns_to_add = ['date', 'average', 'barCount']
                for col in columns_to_add:
                    five_min_df[col] = np.nan

                print('five_min_df columns', five_min_df.columns)
                self.df = pd.concat([self.df, five_min_df])
                print('New 5 minute bar created')

                # Imprimir las 3 últimas barras del DataFrame si hay al menos las 3
                # if len(self.df) >= 3:
                #     print('3 last data frames:', self.df.tail(3))

                # Imprimit el tamaño del DataFrame
                print(f'New DataFrame size: {len(self.df)}')

                plot_only_bars(self.df)

                # Limpiar el buffer y actualizar la última hora de la vela de 5 minutos
                self.buffer_dfs.clear()
                self.last_five_min_time = new_bar.time

                # # Llamar a la estrategia en el nuevo DataFrame
                # action, stop_loss, take_profit = Strategy()(self.df)
                # order = self._evaluate_action(
                #     action, stop_loss, take_profit)

                # if order is not None:
                #     self._execute_order(order)

                # # Eliminar el primer elemento del DataFrame para no consumir demasiada memoria
                # self.df = self.df.iloc[1:]

    def _evaluate_action(self, action: str, stop_loss: float, take_profit: float) -> Optional[List[Order]]:
        if action != 'None':

            # Calcular el tamaño de la posición en lotes
            stop_loss_distance = abs(
                self.df['close'][-1] - stop_loss)  # type: ignore
            position_size_in_lots = BALANCE * RISK / \
                (stop_loss_distance * LOT_PRICE)

            # Crear una orden de stop loss y take profit
            order = self._create_order(
                action, position_size_in_lots, stop_loss, take_profit)

            return order
        return None

    def _create_order(self, action: str, totalQuantity: int, stop_loss: float, take_profit: float) -> List[Order]:
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

        # Retornamos las ordenes en un bracketg
        bracket_order = [parent_order, stop_order, profit_order]

        return bracket_order

    def _execute_order(self, order: List[Order]):
        # Por cada orden en la orden bracket, la colocamos
        for o in order:
            self.ib.placeOrder(self.contract, o)
            print(f'{o.action} {o.orderType} order submitted.')
