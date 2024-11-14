import subprocess
import json

def docker_ps_json():
    try:
        result = subprocess.run(['docker', 'ps', '-a', '--format', '{{json .}}'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        
        containers = []
        for line in lines:
            container = json.loads(line)
            container.pop("Labels", None)  # Eliminar la clave "Labels" si existe
            containers.append(container)
        
        json_output = json.dumps(containers, indent=4)
        return json_output
    
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
        return None

if __name__ == "__main__":
    output = docker_ps_json()
    if output:
        print(output)
