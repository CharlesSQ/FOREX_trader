from typing import Any
from talib import BBANDS, RSI  # type: ignore


class Strategy:
    action: str = ''
    stop_loss: float
    take_profit: float

    def __call__(self, df) -> Any:
        self._get_signal(df)
        self._set_stop_and_limit(df)

        print('action', self.action)
        print('stop_loss', self.stop_loss)
        print('take_profit', self.take_profit)
        return self.action, self.stop_loss, self.take_profit

    def _get_signal(self, df):
        # Calcular las Bandas de Bollinger para el precio de cierre.
        # Las Bandas de Bollinger nos dan una idea de si el precio es alto o bajo en relación con lo que ha sido recientemente.
        df['upper_band'], df['middle_band'], df['lower_band'] = BBANDS(
            df['close'], timeperiod=20)

        # Calcular el Índice de Fuerza Relativa (RSI) para el precio de cierre.
        # El RSI es un indicador de momentum que puede ayudar a identificar si un precio está en una situación de sobrecompra o sobreventa.
        df['RSI'] = RSI(df['close'], timeperiod=14)

        # Señal de compra: si el precio sobrepasa la Banda de Bollinger inferior y el RSI está por debajo de 30
        if df['Low'][-1] < df['lower_band'][-1] and df['RSI'][-1] < 30:
            self.action = "BUY"
        # Señal de venta: si el precio sobrepasa la Banda de Bollinger superior y el RSI está por encima de 70
        elif df['High'][-1] > df['upper_band'][-1] and df['RSI'][-1] > 70:
            self.action = "SELL"
        else:
            self.action = 'None'

    def _set_stop_and_limit(self, df):
        # Definir stop loss y take profit dependiendo de la acción
        self.stop_loss = df['lower_band'][-1] if self.action == 'BUY' else df['upper_band'][-1]

        # Definir take profit igual a la diferencia en pips entre el precio de entrada y el stop loss
        self.take_profit = 2 * df['close'][-1] - self.stop_loss
