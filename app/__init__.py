# app/__init__.py
import os
import logging
import sys
from flask import Flask

def create_app(config_name=None):
    """
    Fábrica de la aplicación Flask.
    Configura y devuelve la instancia de la aplicación.
    """
    app = Flask(__name__)

    # Configuración de Logging
    # El nivel de log se puede controlar con la variable de entorno LOG_LEVEL
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    numeric_log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Configurar el logger raíz y el logger de la app Flask
    # Usar sys.stdout para que los logs sean visibles en contenedores
    logging.basicConfig(stream=sys.stdout,
                        level=numeric_log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Asegurar que el logger de la app Flask también respete el nivel
    # y que el modo debug de Flask se alinee con FLASK_DEBUG.
    is_debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in ("true", "1", "t")
    app.debug = is_debug_mode # Configurar el modo debug de Flask
    
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
        logging.getLogger('werkzeug').setLevel(logging.INFO) # Para ver logs de request/response
    else:
        app.logger.setLevel(logging.INFO)
        logging.getLogger('werkzeug').setLevel(logging.WARNING) # Menos verboso en producción

    app.logger.info(f"Flask app '{app.name}' created. Debug mode: {app.debug}. Log level: {logging.getLevelName(app.logger.getEffectiveLevel())}")


    # Cargar configuración específica si es necesario (ej. desde un config.py)
    # app.config.from_object('config.DefaultConfig')
    # if config_name == 'development':
    #     app.config.from_object('config.DevelopmentConfig')
    # elif config_name == 'production':
    #     app.config.from_object('config.ProductionConfig')

    # Registrar Blueprints
    with app.app_context():
        from .routes import payment_routes # Importar dentro del contexto o al inicio si no hay dependencias circulares
        app.register_blueprint(payment_routes.bp)
        app.logger.info("Payment routes blueprint registered.")

        # Podrías registrar otros blueprints aquí

    app.logger.info("Flask application factory finished setup.")
    return app
