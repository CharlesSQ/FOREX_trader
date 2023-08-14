from typing import Any
from talib import BBANDS, RSI, SMA  # type: ignore


class Strategy:

    action: str = ''
    stop_loss: float
    take_profit: float
    _buy = 'ON'
    _sell = 'ON'
    _buy_signals = []
    _sell_signals = []

    def __call__(self, df) -> Any:
        self._get_signal(df=df)
        self._set_stop_and_limit(df)

        print('action', self.action)
        print('close', df['close'].iloc[-1])
        print('stop_loss', self.stop_loss)
        print('take_profit', self.take_profit)
        return self.action, self.stop_loss, self.take_profit

    def run(self, df) -> Any:
        self._get_signal(self, df=df, test=True)
        self._set_stop_and_limit(df)

        # print('action', self.action)
        # print('close', df['close'].iloc[-1])
        # print('stop_loss', self.stop_loss)
        # print('take_profit', self.take_profit)
        return self.action, self.stop_loss, self.take_profit

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

        # Cálculo de las medias móviles y agregarlas al DataFrame
        df_copy.loc[:, 'SMA20'] = SMA(df_copy['close'].values, timeperiod=100)
        df_copy.loc[:, 'SMA50'] = SMA(df_copy['close'].values, timeperiod=200)

        # print('price', df_copy['close'].iloc[-1])
        # print('higher_band', df_copy['upper_band'].iloc[-1])
        # print('lower_band', df_copy['lower_band'].iloc[-1])
        # print('RSI', df_copy['RSI'].iloc[-1])

        # Señal de compra: si el precio sobrepasa la Banda de Bollinger inferior y el SMA20 cruza por encima del SMA50
        if df_copy['RSI'].iloc[-1] < 30 and df_copy['SMA20'].iloc[-1] > df_copy['SMA50'].iloc[-1]:
            if df_copy['close'].iloc[-1] < df_copy['lower_band'].iloc[-1] and self._buy == 'ON':
                self._buy = 'OFF'
                self.action = "BUY"

                if test:
                    self.buy_signals.append(df_copy.index[-1])
            elif df_copy['close'].iloc[-1] > df_copy['lower_band'].iloc[-1] and self._buy == 'OFF':
                self._buy = 'ON'

        # Señal de venta: si el precio sobrepasa la Banda de Bollinger superior y el SMA20 cruza por debajo del SMA50
        elif df_copy['RSI'].iloc[-1] > 70 and df_copy['SMA20'].iloc[-1] < df_copy['SMA50'].iloc[-1]:
            if df_copy['close'].iloc[-1] > df_copy['upper_band'].iloc[-1] and self._sell == 'ON':
                self._sell = 'OFF'
                self.action = "SELL"

                if test:
                    self.sell_signals.append(df_copy.index[-1])
            elif df_copy['close'].iloc[-1] < df_copy['upper_band'].iloc[-1] and self._sell == 'OFF':
                self._sell = 'ON'
        else:
            self.action = 'None'

    def _set_stop_and_limit(self, df):
        pip_value = 0.0001
        max_pips = 5

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
