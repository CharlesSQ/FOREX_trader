from threading import Timer
from talib import BBANDS, RSI, SMA, EMA  # type: ignore
import plotly.graph_objects as go
import datetime


def plot_bars_Bollinger_RSI(df, buy_signals, sell_signals):
    df['upper_band'], df['middle_band'], df['lower_band'] = BBANDS(
        df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

    df['RSI'] = RSI(df['close'], timeperiod=14)

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])

    # Agregar las Bandas de Bollinger.
    fig.add_trace(go.Scatter(
        x=df.index, y=df['upper_band'], name='Upper Band', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['middle_band'], name='Middle Band', line=dict(color='green')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['lower_band'], name='Lower Band', line=dict(color='magenta')))

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
    fig.add_trace(go.Scatter(
        x=df.index, y=df['RSI'], name='RSI', yaxis='y2', line=dict(color='black')))

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


def plot_bars_Bollinger_RSI_SMA(df, buy_signals, sell_signals):
    df['upper_band'], df['middle_band'], df['lower_band'] = BBANDS(
        df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

    df['RSI'] = RSI(df['close'], timeperiod=14)

    # Cálculo de las medias móviles y agregarlas al DataFrame
    df['SMA100'] = SMA(df['close'].values, timeperiod=100)
    df['SMA200'] = SMA(df['close'].values, timeperiod=200)
    df['SMA400'] = SMA(df['close'].values, timeperiod=400)

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])

    # Agregar las Bandas de Bollinger.
    fig.add_trace(go.Scatter(
        x=df.index, y=df['upper_band'], name='Upper Band', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['middle_band'], name='Middle Band', line=dict(color='green')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['lower_band'], name='Lower Band', line=dict(color='magenta')))

    # Agregar medias moviles
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA100'], name='SMA100', line=dict(color='orange')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA200'], name='SMA200', line=dict(color='gray')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA400'], name='SMA400', line=dict(color='black')))

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
    fig.add_trace(go.Scatter(
        x=df.index, y=df['RSI'], name='RSI', yaxis='y2', line=dict(color='black')))

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


def plot_bars_EMA_RSI(df, buy_signals, sell_signals):
    # Agregar RSI al DataFrame

    df['RSI'] = RSI(df['close'], timeperiod=14)

    # Cálculo de las medias móviles y agregarlas al DataFrame
    df['EMA9'] = EMA(df['close'].values, timeperiod=9)
    df['EMA21'] = EMA(df['close'].values, timeperiod=21)

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])

    # Agregar medias moviles
    fig.add_trace(go.Scatter(
        x=df.index, y=df['EMA9'], name='EMA9', line=dict(color='orange')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['EMA21'], name='EMA21', line=dict(color='gray')))

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
    fig.add_trace(go.Scatter(
        x=df.index, y=df['RSI'], name='RSI', yaxis='y2', line=dict(color='black')))

    # Agregar líneas horizontales para el nivel de 50.
    fig.add_trace(go.Scatter(x=df.index, y=[
                  50] * len(df.index), name='50', yaxis='y2', line=dict(color='red', dash='dash')))

    # Actualizar el diseño para incluir el RSI en una segunda escala de eje y.
    fig.update_layout(
        yaxis=dict(domain=[0.3, 1]),
        yaxis2=dict(domain=[0, 0.2], anchor="x", title="RSI")
    )

    fig.show()


def plot_bars_SMA(df, buy_signals, sell_signals):
    # Cálculo de las medias móviles y agregarlas al DataFrame
    df['SMA20'] = SMA(df['close'].values, timeperiod=100)
    df['SMA50'] = SMA(df['close'].values, timeperiod=200)
    df['SMA400'] = SMA(df['close'].values, timeperiod=400)

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])

    # Agregar medias moviles
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA20'], name='SMA20', line=dict(color='orange')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA50'], name='SMA50', line=dict(color='gray')))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA400'], name='SMA400', line=dict(color='black')))

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

    fig.show()


def plot_only_bars(df):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'])])
    fig.show()


def check_time(callback):
    current_time = datetime.datetime.now()
    if current_time.weekday() == 5 and current_time.hour == 0 and current_time.minute == 0:
        callback()  # Llamar a la función de devolución de llamada (en este caso, ib.disconnect)
    else:
        # Replanificar la verificación para el próximo minuto
        Timer(60, check_time, args=(callback,)).start()
