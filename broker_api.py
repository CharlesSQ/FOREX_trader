from ib_insync import MarketOrder, LimitOrder, StopOrder, Forex


def define_contract(symbol):
    """Define a contract"""
    contract = Forex(symbol)
    return contract


def connect_ib(ib):
    """Connect to IB"""
    ib.connect('127.0.0.1', 7497, clientId=1)


def create_order(action, totalQuantity, stop_loss, take_profit):
    """
    Esta función crea una orden de stop limit para stop loss y una orden limitada para take profit.

    Parámetros:
    - action (str): "BUY" o "SELL", dependiendo de si quieres comprar o vender.
    - totalQuantity (int): la cantidad total que quieres comprar o vender.
    - stop_loss (float): el precio al que quieres vender en caso de que el precio vaya en tu contra.
    - take_profit (float): el precio al que quieres vender en caso de que el precio vaya a tu favor.

    Retorna:
    - bracket_order: una lista de las dos órdenes que componen la orden de soporte (parent, take_profit, stop_loss)
    """

    # Si la acción es comprar, queremos vender para el stop loss y take profit, y viceversa
    opposite_action = "SELL" if action == "BUY" else "BUY"

    # Orden principal (a mercado)
    parent_order = MarketOrder(action, totalQuantity)

    # Orden de Stop Loss (Stop Limit Order)
    stop_order = StopOrder(opposite_action, totalQuantity,
                           stop_loss, parentId=parent_order.orderId, tif='GTC')

    # Orden de Take Profit (Limit Order)
    profit_order = LimitOrder(opposite_action, totalQuantity,
                              take_profit, parentId=parent_order.orderId, tif='GTC')

    # Retornamos las ordenes en un bracket
    bracket_order = [parent_order, stop_order, profit_order]

    return bracket_order
