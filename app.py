import subprocess
import json

def docker_ps_json():
    try:
        # Ejecuta el comando 'docker ps -a'
        result = subprocess.run(['docker', 'ps', '-a', '--format', '{{json .}}'], capture_output=True, text=True, check=True)
        
        # Separa las líneas de la salida
        lines = result.stdout.strip().split('\n')
        
        # Convierte cada línea de JSON a un diccionario
        containers = [json.loads(line) for line in lines]
        
        # Convierte la lista de contenedores a JSON
        json_output = json.dumps(containers, indent=4)
        return json_output
    
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
        return None

if __name__ == "__main__":
    output = docker_ps_json()
    if output:
        print(output)
