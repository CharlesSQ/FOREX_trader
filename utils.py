from threading import Timer
import plotly.graph_objects as go
import datetime


def plot_bars(df, buy_signals, sell_signals):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])

    # Agregar las Bandas de Bollinger.
    fig.add_trace(go.Scatter(
        x=df.index, y=df['upper_band'], name='Upper Band', line=dict(color='blue')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['middle_band'], name='Middle Band', line=dict(color='green')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['lower_band'], name='Lower Band', line=dict(color='red')))

    # Agregar las señales de compra
    for buy_signal in buy_signals:
        fig.add_trace(go.Scatter(x=[buy_signal], y=[df['low'][buy_signal]],
                                 mode='markers', marker=dict(color='green', size=10),
                                 name='Buy Signal'))

    # Agregar las señales de venta
    for sell_signal in sell_signals:
        fig.add_trace(go.Scatter(x=[sell_signal], y=[df['high'][sell_signal]],
                                 mode='markers', marker=dict(color='red', size=10),
                                 name='Sell Signal'))

    # Crear un gráfico separado para el RSI.
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', yaxis='y2'))

    # Agregar líneas horizontales para los niveles de 70 y 30.
    fig.add_trace(go.Scatter(x=df.index, y=[
                  70] * len(df.index), name='Overbought (70)', yaxis='y2', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=[
                  30] * len(df.index), name='Oversold (30)', yaxis='y2', line=dict(color='green', dash='dash')))

    # Actualizar el diseño para incluir el RSI en una segunda escala de eje y.
    fig.update_layout(
        yaxis=dict(domain=[0.3, 1]),
        yaxis2=dict(domain=[0, 0.2], anchor="x", title="RSI")
    )

    fig.show()


def check_time(callback):
    current_time = datetime.datetime.now()
    if current_time.weekday() == 5 and current_time.hour == 0 and current_time.minute == 0:
        callback()  # Llamar a la función de devolución de llamada (en este caso, ib.disconnect)
    else:
        # Replanificar la verificación para el próximo minuto
        Timer(60, check_time, args=(callback,)).start()
