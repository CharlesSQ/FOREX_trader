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
docker run -d --env IB_ACCOUNT=charlesjsq --env IB_PASSWORD=LA@q7Pn\*CFV-\_vg --env TRADE_MODE=paper -p 4002:4002 charlessq/ib-gateway-ibc:v1.2 tail -f /dev/null
