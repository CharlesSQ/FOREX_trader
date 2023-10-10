from typing import Any
from talib import BBANDS, RSI, SMA, EMA  # type: ignore
import plotly.graph_objects as go
import json
import csv
import os


def plot_bars_Bollinger_RSI(df, buy_signals, sell_signals):
    df_copy = df.copy()

    df_copy['upper_band'], df_copy['middle_band'], df_copy['lower_band'] = BBANDS(
        df_copy['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

    df_copy['RSI'] = RSI(df_copy['close'], timeperiod=14)

    fig = go.Figure(data=[go.Candlestick(x=df_copy.index,
                                         open=df_copy['open'],
                                         high=df_copy['high'],
                                         low=df_copy['low'],
                                         close=df_copy['close'])])

    # Agregar las Bandas de Bollinger.
    fig.add_trace(go.Scatter(
        x=df_copy.index, y=df_copy['upper_band'], name='Upper Band', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(
        x=df_copy.index, y=df_copy['middle_band'], name='Middle Band', line=dict(color='green')))
    fig.add_trace(go.Scatter(
        x=df_copy.index, y=df_copy['lower_band'], name='Lower Band', line=dict(color='magenta')))

    # Agregar las señales de compra
    for buy_signal in buy_signals:
        fig.add_trace(go.Scatter(x=[buy_signal], y=[df_copy['low'][buy_signal]],
                                 mode='markers', marker=dict(color='green', size=10),
                                 name='Buy Signal'))

    # Agregar las señales de venta
    for sell_signal in sell_signals:
        fig.add_trace(go.Scatter(x=[sell_signal], y=[df_copy['high'][sell_signal]],
                                 mode='markers', marker=dict(color='red', size=10),
                                 name='Sell Signal'))

    # Crear un gráfico separado para el RSI.
    fig.add_trace(go.Scatter(
        x=df_copy.index, y=df_copy['RSI'], name='RSI', yaxis='y2', line=dict(color='black')))

    # Agregar líneas horizontales para los niveles de 70 y 30.
    fig.add_trace(go.Scatter(x=df_copy.index, y=[
                  70] * len(df_copy.index), name='Overbought (70)', yaxis='y2', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=df_copy.index, y=[
                  30] * len(df_copy.index), name='Oversold (30)', yaxis='y2', line=dict(color='green', dash='dash')))

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
    df['SMA20'] = SMA(df['close'].values, timeperiod=20)
    df['SMA50'] = SMA(df['close'].values, timeperiod=100)
    df['SMA400'] = SMA(df['close'].values, timeperiod=400)

    # Agregar RSI
    df['RSI'] = RSI(df['close'], timeperiod=14)

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


def print_executions_to_csv(executions_by_parent):
    # Abre un archivo en modo append ('a')
    print('Print executions to csv')
    with open('data/ejecuciones.csv', 'a', newline='') as f:
        writer = csv.writer(f)

        # Si el archivo está vacío, añade la fila de encabezado.
        if f.tell() == 0:
            writer.writerow(['Parent ID', 'Action', 'Price', 'Quantity'])

        # Ahora, executions_by_parent contiene las ejecuciones agrupadas por su parentId
        for parent_id, executions in executions_by_parent.items():
            for fill in executions:
                # Escribe cada fila de datos
                writer.writerow([parent_id, fill.execution.side,
                                fill.execution.price, fill.execution.shares])


def print_local_orders_to_csv(order):
    print('Ordenes locales', order)

    # Verificar si el archivo existe
    if not os.path.isfile('data/ordenes_locales.csv'):
        # Si no existe, crearlo y escribir el encabezado
        with open('data/ordenes_locales.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Order ID', 'Action',
                            'Quantity', 'Price', 'Stop Loss', 'Take Profit'])

    # Abre un archivo en modo append ('a')
    with open('data/ordenes_locales.csv', 'a', newline='') as f:
        writer = csv.writer(f)

        # Si el archivo está vacío, añade la fila de encabezado.
        if f.tell() == 0:
            writer.writerow(['Date', 'Order ID', 'Action',
                            'Quantity', 'Price', 'Stop Loss', 'Take Profit'])

        # Escribe cada fila de datos
        writer.writerow([order.date, order.order_id, order.action,
                        order.quantity, order.price, order.stop_loss, order.take_profit])


def set_state(property: str, value: Any):
    data = {}
    with open('data/state.json', 'r') as f:
        data = json.load(f)

    data[property] = value

    with open('data/state.json', 'w') as f:
        json.dump(data, f)


def get_state(property: str):
    data = {}
    with open('data/state.json', 'r') as f:
        data = json.load(f)

    return data[property]
