from ib_insync import IB
from ib_insync import IB, BarData, Contract, MarketOrder, LimitOrder, StopOrder, Order, Forex, util, Ticker
import time

# Crear una instancia de IB()
ib = IB()
print('Conectando a IB')
ib.connect('127.0.0.1', 7497, clientId=1)
contract = Forex('EURUSD')

action = 'SELL'
currentPrice = 1.0717
totalQuantity = 20000
stop_loss = 1.0720
take_profit = 1.0714

opposite_action = "SELL" if action == "BUY" else "BUY"


# Crear y enviar una orden de mercado
market_order = MarketOrder(action, totalQuantity)
print('Placing market order')
trade1 = ib.placeOrder(contract, market_order)
print(f'{market_order.action} {market_order.orderType} order submitted.')
print('trade', trade1.log)

oca_group = f'OCA_{ib.client.getReqId()}'

# Crear y enviar la orden Stop
stop_order = StopOrder(action=opposite_action, totalQuantity=totalQuantity, stopPrice=stop_loss,
                       ocaGroup=oca_group, ocaType=1, tif='GTC')
print('Placing stop order')
trade2 = ib.placeOrder(contract, stop_order)
print(f'{stop_order.action} {stop_order.orderType} order submitted.')
print('trade', trade2.log)

# Crear y enviar la orden Limit
profit_order = LimitOrder(action=opposite_action, totalQuantity=totalQuantity, lmtPrice=take_profit,
                          ocaGroup=oca_group, ocaType=1, tif='GTC')
print('Placing profit order')
trade3 = ib.placeOrder(contract, profit_order)
print(f'{profit_order.action} {profit_order.orderType} order submitted.')
print('trade', trade3.log)

while True:
    ib.sleep(1)
    ib.reqOpenOrders()

    print(
        f'1st Order {market_order.orderId} status: {trade1.orderStatus.status}')

    print(
        f'2nd" Order {stop_order.orderId} status: {trade2.orderStatus.status}')

    print(
        f'3rd Order {profit_order.orderId} status: {trade3.orderStatus.status}')

    if trade1.orderStatus.status == 'Filled' and trade2.orderStatus.status == 'PreSubmitted' and trade3.orderStatus.status == 'PreSubmitted':
        break


# bracket_order = [market_order, stop_order, profit_order]

# # Esperar a que la orden de mercado se llene
# print('Esperando a que la orden de mercado se llene')

# attempt_counter = 0
# MAX_ATTEMPTS = 50

# first_order_filled = False
# for o in bracket_order:
#     try:
#         trade = ib.placeOrder(contract, o)
#         print(f'{o.action} {o.orderType} order submitted.')
#         print('trade', trade.log)
#         if not first_order_filled:
#             while True:
#                 ib.sleep(0.1)
#                 ib.reqOpenOrders()
#                 current_status = trade.orderStatus.status
#                 print(
#                     f'First Order {o.orderId} status: {current_status}')
#                 if current_status == 'Filled':
#                     first_order_filled = True
#                     break
#                 elif current_status in ['Cancelled', 'Rejected']:
#                     print(f'Order was {current_status}. Exiting.')
#                     exit(1)

#                 attempt_counter += 1
#                 if attempt_counter >= MAX_ATTEMPTS:
#                     print('Max attempts reached. Exiting.')
#                     exit(1)

#     except Exception as e:
#         print(f'Error placing order: {e}')
# ib.disconnect()
