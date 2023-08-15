# FXCM_trader

A bot to automate forex trading using scalping method.

quiero crees una aplicación que implemente la siguiente estrategia:
"""
Estrategia de Scalping con Bandas de Bollinger y RSI

Para esta estrategia, utilizaremos las Bandas de Bollinger con los ajustes predeterminados (20 períodos, 2 desviaciones estándar) y el RSI con un periodo de 14. Vamos a usar un gráfico de 5 minutos.

1. Señal de Entrada: Buscamos que el precio toque o sobrepase la Banda de Bollinger superior y que el RSI esté en territorio de sobrecompra (por encima de 70). Cuando estas dos condiciones se cumplen, esto podría ser una señal de que el precio está a punto de retroceder, y podríamos abrir una posición corta (venta).

De manera opuesta, si el precio toca o sobrepasa la Banda de Bollinger inferior y el RSI está en territorio de sobreventa (por debajo de 30), esto podría ser una señal de que el precio está a punto de repuntar, y podríamos abrir una posición larga (compra).

2. Stop loss: Establecer el stop loss justo más allá de la Banda de Bollinger que fue tocada o sobrepasada en la señal de entrada.
   Para una operación de venta: Si entraste en una operación de venta porque el precio tocó o sobrepasó la Banda de Bollinger superior y el RSI estaba en territorio de sobrecompra, podrías colocar tu stop-loss unos pocos pips por encima de la Banda de Bollinger superior.

   Para una operación de compra: Si entraste en una operación de compra porque el precio tocó o sobrepasó la Banda de Bollinger inferior y el RSI estaba en territorio de sobreventa, podrías colocar tu stop-loss unos pocos pips por debajo de la Banda de Bollinger inferior.

3. Limite: Cerrar la posición cuando los pips ganados sean igual a la diferencia en pips del precio de entrada y el stop loss.

Comenta todo el codigo y utiliza buenas practicas de programación en python.
"""
Pruebas Saldo Variación %
Semana 0 200 0
Semana 1 228 14
Semana 2 246 7.9
Semana 3 283 15
Semana 4 326 15.2
Semana 5 348 6.7
Semana 6 401 15.2
Semana 7 377 -6
Semana 8 422 11.9
Semana 9 553 31
Semana 10 569 2.9
Semana 11 626 10
Semana 12 632 1
Semana 13 670 6
Semana 14 771 15
Semana 15 755 -2.1
Semana 16 944 25
Semana 17 992 5.1
Semana 18 1120 12.1
Semana 19 1076 -3.9
Semana 20 1280 19
Semana 21 1306 2
Semana 22 1397 7
Semana 23 1481 6
Semana 24 1510 2
Semana 25 1405 -7
Semana 26 1489 6
Semana 27 2025 36
Semana 28 2309 14
Semana 29 2424 5
Semana 30 2836 17
Semana 31 3347 18
