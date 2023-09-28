import datetime
from ib_insync import IB, BarData, Contract, MarketOrder, LimitOrder, StopOrder, Forex, util, Ticker
from typing import List, Optional
from collections import deque
from dataclasses import dataclass
from strategies.bollinger_RSI import Strategy
from constants import BALANCE, RISK
# from utils import plot_bars_Bollinger_RSI, print_local_orders_to_csv
from utils import print_local_orders_to_csv
import pandas as pd
import numpy as np
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="[%(asctime)s]%(levelname)s:%(message)s")


@dataclass
class Order:
    date: str
    order_id: int
    action: str
    quantity: int
    price: float
    stop_loss: float
    take_profit: float


class Trader:
    _all_orders: List[Order] = []

    def __init__(self, ib: IB, contract: Contract, bars: List[BarData]):
        logging.info('Inicializando Trader...')
        self.ib = ib
        self.contract = contract
        self.df = util.df(bars)
        self.df.drop('date', axis=1, inplace=True)
        self.buffer_dfs = deque()
        self.current_orders: int = 0
        self.strategy = Strategy()
        self.current_bid = None
        self.current_ask = None

    @staticmethod
    def define_contract(symbol: str) -> Contract:
        """Define a contract"""
        logging.info(f'Definiendo contrato para {symbol}...')
        contract = Forex(symbol)
        return contract

    def connect_ib(ib: IB):
        """Connect to IB"""
        logging.info('Conectando a Interactive Brokers...')
        # ib.connect('localhost', 4002, clientId=2)
        ib.connect('ib_gateway', 4002, clientId=999)

    def on_ticker_update(self, ticker: Ticker):
        self.current_bid = ticker.bid
        self.current_ask = ticker.ask

    def subscribe_ticker(self):
        """Suscribir al ticker y manejar las actualizaciones"""
        logging.info('Subscribiendo al ticker...')
        self.ticker = self.ib.reqMktData(self.contract, '', False, False)
        self.ticker.updateEvent += self.on_ticker_update

    def on_bar_update(self, bars: List[BarData], has_new_bar: bool):
        """
        Esta función se ejecuta cada vez que se recibe una nueva barra de datos en tiempo real.

        Args:
            bars (List[BarData]): Lista de objetos BarData que representa las barras de datos en tiempo real recibidas hasta el momento.
            has_new_bar (bool): Un indicador booleano que señala si la última actualización incluye una nueva barra. Si es True, la última barra en 'bars' es una nueva barra. Si es False, la última barra en 'bars' se ha actualizado con nuevos datos.

        Dentro de la función, se comprueba si se ha recibido una nueva barra. Si es así, se extrae la última barra (la nueva barra) de 'bars'. Esta nueva barra se puede utilizar para realizar cálculos adicionales, generar señales de trading, o cualquier otra tarea que necesites.
        """
        if has_new_bar:
            new_bar = bars[-1]
            # Convertir el nuevo bar en un DataFrame y añadirlo al buffer
            new_df = util.df([new_bar])
            self.buffer_dfs.append(new_df)

            # Si buffer_dfs tiene 60 barras, crear una nueva vela de 5 minutos
            FIVE_SEC_BARS = 5
            if (len(self.buffer_dfs) == FIVE_SEC_BARS):

                # Crear una nueva vela de 5 minutos a partir del buffer y añadirla al DataFrame
                five_sec_df = pd.concat(self.buffer_dfs)

                data = {
                    'open': five_sec_df['open_'].iloc[0],
                    'high': five_sec_df['high'].max(),
                    'low': five_sec_df['low'].min(),
                    'close': five_sec_df['close'].iloc[-1],
                    'volume': five_sec_df['volume'].iloc[-1]
                }

                five_min_df = pd.DataFrame([data])

                columns_to_add = ['average', 'barCount']
                for col in columns_to_add:
                    five_min_df[col] = np.nan

                next_index = self.df.index[-1] + 1
                five_min_df.index = [next_index]

                self.df = pd.concat([self.df, five_min_df])

                logging.info('\n')
                # print(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]')
                logging.info(f'nueva barra de 5 min:\n {self.df.tail(2)}')

                # Limpiar el buffer y actualizar la última hora de la vela de 5 minutos
                self.buffer_dfs.clear()

                # Llamar a la estrategia en el nuevo DataFrame
                logging.info('Llamando a la estrategia...')
                action, stop_loss, take_profit = self.strategy.run(self.df)
                logging.info(f'Acción: {action}')

                if action != 'None':
                    position_size_in_lot_units, adjusted_stop_loss, adjusted_take_profit = self._evaluate_action(
                        action, stop_loss, take_profit)

                    self._place_orders(action=action, totalQuantity=position_size_in_lot_units,
                                       stop_loss=adjusted_stop_loss, take_profit=adjusted_take_profit)

                # Eliminar el primer elemento del DataFrame para no consumir demasiada memoria
                self.df = self.df.iloc[1:]

    def _evaluate_action(self, action: str, stop_loss: float, take_profit: float) -> Optional[List[Order]]:
        """
        Esta función evalúa la acción de la estrategia y devuelve el tamaño de la posición en lotes, el precio de stop loss y el precio de take profit.
        """
        logging.info('Evaluate action...')
        LOT_PRICE = 10
        LOT_SIZE = 100000

        # plot_bars_Bollinger_RSI(
        #     self.df, self.strategy.buy_signals, self.strategy.sell_signals)

        # Calcular el spread
        spread: float = round(self.current_ask - self.current_bid, 5)
        logging.info(f"Spread actual: {spread}")
        logging.info(f'Precio de cierre: {self.df["close"].iloc[-1]}')
        logging.info(f'Precio de stop_loss: {stop_loss}')
        logging.info(f'Precio de take_profit: {take_profit}')

        # Ajustar el stop loss y take profit para tener en cuenta el spread
        if action == 'BUY':
            adjusted_stop_loss = round(stop_loss - spread, 5)
            adjusted_take_profit = round(take_profit + spread, 5)
        else:
            adjusted_stop_loss = round(stop_loss + spread, 5)
            adjusted_take_profit = round(take_profit - spread, 5)

        logging.info(f'Stop loss ajustado: {adjusted_stop_loss}')
        logging.info(f'Take profit ajustado: {adjusted_take_profit}')

        # Calcular el tamaño de la posición en lotes
        stop_loss_distance = round(abs(
            self.df['close'].iloc[-1] - adjusted_stop_loss) * 10000, 3)
        logging.info(f'Distancia al stop loss: {stop_loss_distance}')

        position_size_in_lot_units = round(BALANCE * RISK /
                                           (stop_loss_distance * LOT_PRICE) * LOT_SIZE)
        logging.info(
            f'Tamaño de la posicion en unidades de lote: {position_size_in_lot_units}')

        return position_size_in_lot_units, adjusted_stop_loss, adjusted_take_profit

    def _place_orders(self, action: str, totalQuantity: int, stop_loss: float, take_profit: float) -> List[Order]:
        """
        Esta función crea y envía una orden de mercado, una orden stop loss y una orden take profit al broker.
        Parametros:
            action (str): La acción de la orden. Puede ser 'BUY' o 'SELL'.
            totalQuantity (int): El tamaño de la posición en lotes.
            stop_loss (float): El precio de stop loss.
            take_profit (float): El precio de take profit.
        """
        opposite_action = "SELL" if action == "BUY" else "BUY"

        try:
           # Crear y enviar una orden de mercado
            market_order = MarketOrder(action, totalQuantity)
            logging.info('Colocando market order')
            trade1 = self.ib.placeOrder(self.contract, market_order)
            logging.info(
                f'{market_order.action} {market_order.orderType} orden enviada.')
            logging.info(f'market order: {trade1.log}')

            oca_group = f'OCA_{self.ib.client.getReqId()}'

            # Crear y enviar la orden Stop
            stop_order = StopOrder(action=opposite_action, totalQuantity=totalQuantity, stopPrice=stop_loss,
                                   ocaGroup=oca_group, ocaType=1, tif='GTC')
            logging.info('Colocando stop order')
            trade2 = self.ib.placeOrder(self.contract, stop_order)
            logging.info(
                f'{stop_order.action} {stop_order.orderType} orden enviada.')
            logging.info(f'stop order: {trade2.log}')

            # Crear y enviar la orden Limit
            profit_order = LimitOrder(action=opposite_action, totalQuantity=totalQuantity, lmtPrice=take_profit,
                                      ocaGroup=oca_group, ocaType=1, tif='GTC')
            logging.info('Colocando profit order')
            trade3 = self.ib.placeOrder(self.contract, profit_order)
            logging.info(
                f'{profit_order.action} {profit_order.orderType} orden enviada.')
            logging.info(f'profit order: {trade3.log}')

            # Añadir las órdenes a la lista de órdenes
            self._add_order_to_list(market_order.orderId, action, totalQuantity,
                                    self.df['close'].iloc[-1], stop_loss, take_profit)

        except Exception as e:
            logging.info(f'Error al colocar orden: {e}')

    def _add_order_to_list(self, order_id, action, quantity, price, stop_loss, take_profit):
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # Create order object
        order_object: Order = Order(
            date, order_id, action, quantity, price, stop_loss, take_profit)

        # Add order to current orders
        self._all_orders.append(order_object)

        # Print orders to csv
        print_local_orders_to_csv(order_object)

    @property
    def all_orders(self):
        return self._all_orders
