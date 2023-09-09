from ib_insync import IB
from datetime import datetime
from utils import print_executions_to_csv


def get_executions(ib: IB):
    current_time = datetime.now()
    current_time_str = current_time.strftime('%H:%M')
    if current_time_str == '15:58':
        # Obtener las ejecuciones recientes
        print('Obteniendo ejecuciones recientes')
        executions = ib.reqExecutions()
        print(f'Encontradas {len(executions)} ejecuciones')

        if len(executions) == 0:
            print('No se encontraron ejecuciones')
            exit(1)
        else:
            # Crear un diccionario para agrupar las ejecuciones por parentId
            executions_by_parent = {}

            # Iterar sobre las ejecuciones
            print('Agrupando ejecuciones por parentId')
            for fill in executions:
                # El campo orderId en una ejecución es equivalente al parentId de la orden original
                parent_id = fill.execution.orderId
                if parent_id not in executions_by_parent:
                    executions_by_parent[parent_id] = []
                executions_by_parent[parent_id].append(fill)

            print_executions_to_csv(executions_by_parent)

            print('Imprimiendo ejecuciones')
            for parent_id, executions in executions_by_parent.items():
                print(f'Parent ID: {parent_id}')
                for fill in executions:
                    print(
                        f' Action: {fill.execution.side}, Price: {fill.execution.price}, Quantity: {fill.execution.shares}')
