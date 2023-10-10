from typing import Any
from talib import SMA, RSI  # type: ignore


class Strategy:

    action: str = ''
    stop_loss: float
    take_profit: float
    _RSI_overbought_cross = ''
    _RSI_oversold_cross = ''
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

        # Cálculo de las medias móviles y agregarlas al DataFrame
        df_copy.loc[:, 'SMA20'] = SMA(df_copy['close'].values, timeperiod=20)
        df_copy.loc[:, 'SMA50'] = SMA(df_copy['close'].values, timeperiod=100)
        df_copy.loc[:, 'SMA400'] = SMA(df_copy['close'].values, timeperiod=400)

        # Calcular el Índice de Fuerza Relativa (RSI) para el precio de cierre.
        # El RSI es un indicador de momentum que puede ayudar a identificar si un precio está en una situación de sobrecompra o sobreventa.
        df_copy.loc[:, 'RSI'] = RSI(df_copy['close'], timeperiod=14)

        # Evaluar si el RSI cruza por debajo de 70
        if self._RSI_overbought_cross == 'ABOVE_70' and df_copy['RSI'].iloc[-1] < 70:
            self._RSI_overbought_cross = 'CROSS_BELOW_70'
        elif self._RSI_overbought_cross == 'CROSS_BELOW_70' and df_copy['RSI'].iloc[-1] > df_copy['RSI'].iloc[-2]:
            self._RSI_overbought_cross = ''
        elif df_copy['RSI'].iloc[-1] > 70:
            self._RSI_overbought_cross = 'ABOVE_70'

        # Evaluar si el RSI cruza por encima de 30
        if self._RSI_oversold_cross == 'BELOW_30' and df_copy['RSI'].iloc[-1] > 30:
            self._RSI_oversold_cross = 'CROSS_ABOVE_30'
        elif self._RSI_oversold_cross == 'CROSS_ABOVE_30' and df_copy['RSI'].iloc[-1] < df_copy['RSI'].iloc[-2]:
            self._RSI_oversold_cross = ''
        elif df_copy['RSI'].iloc[-1] < 30:
            self._RSI_oversold_cross = 'BELOW_30'

        # Señal de compra: si el precio sobrepasa la Banda de Bollinger inferior y el SMA20 cruza por encima del SMA50
        if df_copy['SMA20'].iloc[-1] > (df_copy['SMA50'].iloc[-1] + 0.00025) and df_copy['SMA50'].iloc[-1] > (df_copy['SMA400'].iloc[-1] + 0.00025) and \
                df_copy['RSI'].iloc[-1] < 40:
            if df_copy['low'].iloc[-1] < df_copy['SMA20'].iloc[-1] and self._buy == 'ON':
                self._buy = 'OFF'
                self.action = "BUY"

                if test:
                    self.buy_signals.append(df_copy.index[-1])
            elif df_copy['close'].iloc[-1] > df_copy['SMA20'].iloc[-1] and self._buy == 'OFF':
                self._buy = 'ON'

        # Señal de venta: si el precio sobrepasa la Banda de Bollinger superior y el SMA20 cruza por debajo del SMA50
        elif df_copy['SMA20'].iloc[-1] < (df_copy['SMA50'].iloc[-1] - 0.00025) and df_copy['SMA50'].iloc[-1] < (df_copy['SMA400'].iloc[-1] - 0.00025) and \
                df_copy['RSI'].iloc[-1] > 60:
            if df_copy['high'].iloc[-1] > df_copy['SMA20'].iloc[-1] and self._sell == 'ON':
                self._sell = 'OFF'
                self.action = "SELL"

                if test:
                    self.sell_signals.append(df_copy.index[-1])
            elif df_copy['close'].iloc[-1] < df_copy['SMA20'].iloc[-1] and self._sell == 'OFF':
                self._sell = 'ON'

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
