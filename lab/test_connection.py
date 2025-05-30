from ib_insync import *
from concurrent.futures import TimeoutError

ib = IB()
wait = 60
while not ib.isConnected():
    try:
        IB.sleep(1)
        ib.connect('localhost', 4002, clientId=999)
    except (ConnectionRefusedError, OSError, TimeoutError):
        pass
    wait -= 1
    if wait <= 0:
        break
if ib.isConnected():
    print('ib is connected')
else:
    print('Cannot connect to IB')

ib.disconnect()
