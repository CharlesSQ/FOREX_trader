from typing import Any
from talib import BBANDS, RSI  # type: ignore
from .utils import get_state, set_state


class Strategy:

    action: str = ''
    stop_loss: float = 0
    take_profit: float = 0
    price_close: float = 0
    _buy: str
    _sell: str
    _buy_signals = []
    _sell_signals = []
    _test: bool = False

    def __init__(self, test=False) -> None:
        if test:
            self._buy = 'ON'
            self._sell = 'ON'
            self._test = True
        else:
            self._buy = get_state('_buy')
            self._sell = get_state('_sell')

    def run(self, df) -> Any:
        """Ejecuta la estrategia en el DataFrame proporcionado."""
        self._get_signal(self, df=df, test=self._test)
        if self.action != 'None':
            self._set_stop_and_limit(df)

        # print('action', self.action)
        # print('close', df['close'].iloc[-1])
        # print('stop_loss', self.stop_loss)
        # print('take_profit', self.take_profit)
        return self.action, self.stop_loss, self.take_profit, self.price_close

    @staticmethod
    def _get_signal(self, df, test=False):
        df_copy = df.copy()

        # Calcular las Bandas de Bollinger para el precio de cierre. Configuración estándar (20 períodos para la media móvil y 2 desviaciones estándar)..
        # Las Bandas de Bollinger nos dan una idea de si el precio es alto o bajo en relación con lo que ha sido recientemente.
        df_copy.loc[:, 'upper_band'], df_copy.loc[:, 'middle_band'], df_copy.loc[:,
                                                                                 'lower_band'] = BBANDS(df_copy['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

        # Calcular el Índice de Fuerza Relativa (RSI) para el precio de cierre.
        # El RSI es un indicador de momentum que puede ayudar a identificar si un precio está en una situación de sobrecompra o sobreventa.
        df_copy.loc[:, 'RSI'] = RSI(df_copy['close'], timeperiod=14)

        # Señal de compra: si el precio sobrepasa la Banda de Bollinger inferior y el RSI cruza por encima de 30
        if df_copy['RSI'].iloc[-1] < 30:
            if df_copy['close'].iloc[-1] < df_copy['lower_band'].iloc[-1] and self._buy == 'ON':
                self._buy = 'OFF'
                self.action = "BUY"
                self.price_close = df_copy['close'].iloc[-1]
                set_state('_buy', self._buy)

            elif df_copy['close'].iloc[-1] > df_copy['lower_band'].iloc[-1] and self._buy == 'OFF':
                self._buy = 'ON'
                self.action = 'None'
                set_state('_buy', self._buy)
            else:
                self.action = 'None'

            if test and self.action == 'BUY':
                self.buy_signals.append(df_copy.index[-1])

        # Señal de venta: si el precio sobrepasa la Banda de Bollinger superior y el RSI cruza por debajo de 70
        elif df_copy['RSI'].iloc[-1] > 70:
            if df_copy['close'].iloc[-1] > df_copy['upper_band'].iloc[-1] and self._sell == 'ON':
                self._sell = 'OFF'
                self.action = "SELL"
                self.price_close = df_copy['close'].iloc[-1]
                set_state('_sell', self._sell)

            elif df_copy['close'].iloc[-1] < df_copy['upper_band'].iloc[-1] and self._sell == 'OFF':
                self._sell = 'ON'
                self.action = 'None'
                set_state('_sell', self._sell)
            else:
                self.action = 'None'

            if test and self.action == 'SELL':
                self.sell_signals.append(df_copy.index[-1])

        else:
            self.action = 'None'

    def _set_stop_and_limit(self, df):
        pip_value = 0.0001
        max_pips = 10

        # Obtener el precio de cierre más reciente
        latest_close = df['close'].iloc[-1]

        # Calcular los precios con +10 y -10 pips
        upper_bound = latest_close + pip_value * max_pips
        lower_bound = latest_close - pip_value * max_pips

        # Definir stop loss y take profit dependiendo de la acción
        self.stop_loss = lower_bound if self.action == 'BUY' else upper_bound
        self.take_profit = upper_bound if self.action == 'BUY' else lower_bound

    @property
    def buy_signals(self):
        return self._buy_signals

    @property
    def sell_signals(self):
        return self._sell_signals
