from ib_insync import IB, ExecutionFilter
from datetime import datetime, timedelta

# Conectar con Interactive Brokers
ib = IB()
print('Conectando a IB')
ib.connect('127.0.0.1', 7497, clientId=1)

# Obtener la fecha de hace 5 días
five_days_ago = datetime.now() - timedelta(days=5)
five_days_ago_str = five_days_ago.strftime('%Y%m%d %H:%M:%S')

# Crear un filtro para los últimos 5 días
execution_filter = ExecutionFilter(time=five_days_ago_str)

# Obtener las ejecuciones recientes
print('Obteniendo ejecuciones recientes')
executions = ib.reqExecutions(execution_filter)
print(f'Encontradas {len(executions)} ejecuciones')

if len(executions) == 0:
    print('No se encontraron ejecuciones')
    exit(1)
else:
    # Crear un diccionario para agrupar las ejecuciones por parentId
    executions_by_parent = {}

    # Iterar sobre las ejecuciones
    print('Agrupando ejecuciones por parentId')
    for execution in executions:
        # El campo orderId en una ejecución es equivalente al parentId de la orden original
        parent_id = execution.orderId
        if parent_id not in executions_by_parent:
            executions_by_parent[parent_id] = []
        executions_by_parent[parent_id].append(execution)

    # Ahora, executions_by_parent contiene las ejecuciones agrupadas por su parentId
    print('Imprimiendo ejecuciones')
    for parent_id, executions in executions_by_parent.items():
        print(f'Parent ID: {parent_id}')
        for execution in executions:
            print(
                f' Action: {execution.side}, Price: {execution.price}, Quantity: {execution.shares}')
