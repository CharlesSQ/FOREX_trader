from typing import Any
from talib import BBANDS, RSI, EMA  # type: ignore


class Strategy:

    action: str = ''
    stop_loss: float
    take_profit: float
    _EMA9 = 'CROSS_UP'
    _EMA9_CROSS_UP_COUNT = 0
    _EMA9_CROSS_DOWN_COUNT = 0
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

        # Calcular el Índice de Fuerza Relativa (RSI) para el precio de cierre.
        # El RSI es un indicador de momentum que puede ayudar a identificar si un precio está en una situación de sobrecompra o sobreventa.
        df_copy.loc[:, 'RSI'] = RSI(df_copy['close'], timeperiod=14)

        # Cálculo de las medias móviles y agregarlas al DataFrame
        df_copy.loc[:, 'EMA9'] = EMA(df_copy['close'].values, timeperiod=9)
        df_copy.loc[:, 'EMA21'] = EMA(df_copy['close'].values, timeperiod=21)

        # EMA9 cruza por encima de EMA21
        if df_copy['EMA9'].iloc[-1] > df_copy['EMA21'].iloc[-1]:
            self._EMA9 = 'CROSS_UP'
            self._EMA9_CROSS_UP_COUNT += 1
            self._EMA9_CROSS_DOWN_COUNT = 0
        elif df_copy['EMA9'].iloc[-1] < df_copy['EMA21'].iloc[-1]:
            self._EMA9 = 'CROSS_DOWN'
            self._EMA9_CROSS_DOWN_COUNT += 1
            self._EMA9_CROSS_UP_COUNT = 0

        # print('price', df_copy['close'].iloc[-1])
        # print('higher_band', df_copy['upper_band'].iloc[-1])
        # print('lower_band', df_copy['lower_band'].iloc[-1])
        # print('RSI', df_copy['RSI'].iloc[-1])

        # Señal de compra: si el precio sobrepasa la Banda de Bollinger inferior y el SMA20 cruza por encima del SMA50
        if df_copy['EMA9'].iloc[-1] > df_copy['EMA21'].iloc[-1] and df_copy['RSI'].iloc[-1] > 50 and \
                self._EMA9 == 'CROSS_UP' and self._EMA9_CROSS_UP_COUNT == 1:

            # Vela alcista
            if df_copy['close'].iloc[-1] > df_copy['open'].iloc[-1]:
                self.action = "BUY"

            if test:
                self.buy_signals.append(df_copy.index[-1])

        # Señal de venta: si el precio sobrepasa la Banda de Bollinger superior y el SMA20 cruza por debajo del SMA50
        elif df_copy['EMA9'].iloc[-1] < df_copy['EMA21'].iloc[-1] and df_copy['RSI'].iloc[-1] < 50 and \
                self._EMA9 == 'CROSS_DOWN' and self._EMA9_CROSS_DOWN_COUNT == 1:

            # Vela bajista
            if df_copy['close'].iloc[-1] < df_copy['open'].iloc[-1]:
                self.action = "SELL"

            if test:
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
