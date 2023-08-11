from typing import Any
from talib import BBANDS, RSI  # type: ignore


class Strategy:

    action: str = ''
    stop_loss: float
    take_profit: float
    _buy_signals = []
    _sell_signals = []

    def __call__(self, df) -> Any:
        self._get_signal(df=df)
        self._get_signal(df)
        self._set_stop_and_limit(df)

        print('action', self.action)
        print('stop_loss', self.stop_loss)
        print('take_profit', self.take_profit)
        return self.action, self.stop_loss, self.take_profit

    def run(self, df) -> Any:
        self._get_signal(self, df=df, test=True)
        self._set_stop_and_limit(df)

        print('action', self.action)
        print('stop_loss', self.stop_loss)
        print('take_profit', self.take_profit)
        return self.action, self.stop_loss, self.take_profit

    @staticmethod
    def _get_signal(self, df, test=False):
        df_copy = df.copy()

        # Calcular las Bandas de Bollinger para el precio de cierre.
        # Las Bandas de Bollinger nos dan una idea de si el precio es alto o bajo en relación con lo que ha sido recientemente.
        df_copy.loc[:, 'upper_band'], df_copy.loc[:, 'middle_band'], df_copy.loc[:,
                                                                                 'lower_band'] = BBANDS(df_copy['close'], timeperiod=20)

        # Calcular el Índice de Fuerza Relativa (RSI) para el precio de cierre.
        # El RSI es un indicador de momentum que puede ayudar a identificar si un precio está en una situación de sobrecompra o sobreventa.
        # df_copy['RSI'] = RSI(df_copy['close'], timeperiod=14)
        df_copy.loc[:, 'RSI'] = RSI(df_copy['close'], timeperiod=14)

        # Señal de compra: si el precio sobrepasa la Banda de Bollinger inferior y el RSI está por debajo de 30
        print('price', df_copy['close'].iloc[-1])
        print('higher_band', df_copy['upper_band'].iloc[-1])
        print('lower_band', df_copy['lower_band'].iloc[-1])
        print('RSI', df_copy['RSI'].iloc[-1])

        if df_copy['close'].iloc[-1] < df_copy['lower_band'].iloc[-1] and df_copy['RSI'].iloc[-1] < 30:
            self.action = "BUY"

            if test:
                self.buy_signals.append(df_copy.index[-1])

        # Señal de venta: si el precio sobrepasa la Banda de Bollinger superior y el RSI está por encima de 70
        elif df_copy['close'].iloc[-1] > df_copy['upper_band'].iloc[-1] and df_copy['RSI'].iloc[-1] > 70:
            self.action = "SELL"

            if test:
                self.sell_signals.append(df_copy.index[-1])

        else:
            self.action = 'None'

    def _set_stop_and_limit(self, df):
        # Definir stop loss y take profit dependiendo de la acción
        self.stop_loss = df['lower_band'].iloc[-1] if self.action == 'BUY' else df['upper_band'].iloc[-1]

        # Definir take profit igual a la diferencia en pips entre el precio de entrada y el stop loss
        self.take_profit = 2 * df['close'].iloc[-1] - self.stop_loss

    @property
    def buy_signals(self):
        return self._buy_signals

    @property
    def sell_signals(self):
        return self._sell_signals
