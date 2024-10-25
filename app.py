import subprocess
import prettytable as pt

def get_docker_containers():
    # Ejecuta el comando docker ps -a para obtener la lista de contenedores
    result = subprocess.run(['docker', 'ps', '-a'], stdout=subprocess.PIPE)
    
    # Decodifica la salida del comando
    output = result.stdout.decode('utf-8')
    
    # Divide las líneas de la salida
    lines = output.splitlines()
    
    # El encabezado es la primera línea
    header = lines[0].split()
    
    # El resto son los contenedores
    containers = lines[1:]
    
    # Usa PrettyTable para mostrar los datos en un formato más legible
    table = pt.PrettyTable(header)
    
    for container in containers:
        # Divide la línea en columnas
        columns = container.split(maxsplit=len(header) - 1)
        table.add_row(columns)
    
    print(table)

if __name__ == "__main__":
    get_docker_containers()
