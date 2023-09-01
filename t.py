from ib_insync import IB
from ib_insync import IB, BarData, Contract, MarketOrder, LimitOrder, StopOrder, Order, Forex, util, Ticker
import time

# Crear una instancia de IB()
ib = IB()
print('Conectando a IB')
ib.connect('127.0.0.1', 7497, clientId=1)
contract = Forex('EURUSD')

action = 'BUY'
currentPrice = 1.0774
totalQuantity = 25000
stop_loss = 1.0772
take_profit = 1.0778

opposite_action = "SELL" if action == "BUY" else "BUY"

print('Creando ordene de mercado')

# Crear y enviar una orden de mercado
parent_order = MarketOrder(action, totalQuantity)

oca_group = f'OCA_{ib.client.getReqId()}'

# Crear y enviar la orden Stop
stop_order = StopOrder(action=opposite_action, totalQuantity=totalQuantity, stopPrice=stop_loss,
                       ocaGroup=oca_group, ocaType=1, parentId=parent_order.orderId, tif='GTC')

# Crear y enviar la orden Limit
profit_order = LimitOrder(action=opposite_action, totalQuantity=totalQuantity, lmtPrice=take_profit,
                          ocaGroup=oca_group, ocaType=1, parentId=parent_order.orderId, tif='GTC')

bracket_order = [parent_order, stop_order, profit_order]

# Esperar a que la orden de mercado se llene
print('Esperando a que la orden de mercado se llene')

attempt_counter = 0
MAX_ATTEMPTS = 10

first_order_filled = False
for o in bracket_order:
    try:
        trade = ib.placeOrder(contract, o)
        print(f'{o.action} {o.orderType} order submitted.')
        print('trade', trade.log)
        if not first_order_filled:
            while True:
                ib.sleep(0.1)
                ib.reqOpenOrders()
                current_status = trade.orderStatus.status
                if current_status == 'Filled':
                    first_order_filled = True
                    print(
                        f'First Order {o.orderId} status: {current_status}')
                    break
                elif current_status in ['Cancelled', 'Rejected']:
                    print(f'Order was {current_status}. Exiting.')
                    exit(1)

                attempt_counter += 1
                if attempt_counter >= MAX_ATTEMPTS:
                    print('Max attempts reached. Exiting.')
                    exit(1)

    except Exception as e:
        print(f'Error placing order: {e}')
