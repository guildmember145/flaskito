# run.py
import os
from dotenv import load_dotenv
from app import create_app # Importar la fábrica de aplicaciones

# Cargar variables de entorno desde .env al inicio, si existe.
# Esto es principalmente para desarrollo local. En contenedores, las variables
# se inyectan directamente en el entorno del contenedor.
# Asumimos que .env está en el mismo directorio que run.py (raíz del proyecto)
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(dotenv_path):
    print(f"Loading .env file from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path, verbose=True)
else:
    print(f"No .env file found at {dotenv_path}. Using system/container environment variables.")

# Crear la instancia de la aplicación usando la fábrica
application = create_app()

if __name__ == '__main__':
    # Obtener configuraciones del entorno para el servidor de desarrollo de Flask
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    
    port_str = os.environ.get("FLASK_RUN_PORT", "8000") # Obtener como string
    try:
        # Limpiar posibles comillas y espacios antes de convertir a int
        port = int(port_str.strip().strip("'").strip('"'))
    except ValueError:
        print(f"Advertencia: Valor inválido para FLASK_RUN_PORT ('{port_str}'). Usando puerto por defecto 8000.")
        port = 8000
            
    debug_env = os.environ.get("FLASK_DEBUG", "0") 
    debug_mode = debug_env.lower() in ("true", "1", "t")

    print(f"Starting development server on http://{host}:{port}/, debug: {debug_mode}")
    application.run(host=host, port=port, debug=debug_mode)
