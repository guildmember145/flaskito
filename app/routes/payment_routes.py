# app/routes/payment_routes.py
from flask import Blueprint, request, jsonify, current_app
from app.services import khipu_service # Importar el servicio de Khipu

# Crear un Blueprint para las rutas de pago
# El primer argumento es el nombre del blueprint, el segundo es el __name__ del módulo,
# y url_prefix antepondrá '/api/khipu' (o lo que elijas) a todas las rutas de este blueprint.
# Dado que tus rutas originales eran /v3/payments, usaremos /v3 como prefijo.
bp = Blueprint('payments', __name__, url_prefix='/v3')

@bp.route('/payments', methods=['POST'])
def handle_create_payment():
    """
    Manejador de la ruta para crear un nuevo pago a través de Khipu.
    """
    if not request.is_json:
        current_app.logger.warning("Solicitud a /v3/payments no es JSON.")
        return jsonify({"error": "El cuerpo de la solicitud debe ser JSON"}), 400

    client_data = request.get_json()
    current_app.logger.info(f"Ruta /v3/payments recibió datos: {client_data}")

    try:
        khipu_response = khipu_service.create_payment_intent(client_data)
        # Si create_payment_intent es exitoso, devuelve los datos de Khipu y un 201.
        return jsonify(khipu_response), 201
    except khipu_service.KhipuConfigError as e:
        current_app.logger.error(f"Error de configuración de Khipu: {e}")
        return jsonify({"error": str(e)}), e.status_code or 500
    except khipu_service.KhipuServiceError as e: # Captura KhipuRequestError, KhipuConnectionError también
        current_app.logger.error(f"Error del servicio Khipu: {e} - Data: {e.khipu_response_data}")
        # Devolver el error de Khipu si está disponible y es un diccionario (JSON)
        if isinstance(e.khipu_response_data, dict):
            return jsonify(e.khipu_response_data), e.status_code or 400
        else: # Sino, un error genérico con el mensaje
            return jsonify({"error": str(e), "details": e.khipu_response_data}), e.status_code or 400
    except Exception as e: # Captura cualquier otra excepción inesperada
        current_app.logger.error(f"Error inesperado en la ruta de creación de pago: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor al procesar el pago"}), 500


@bp.route('/health_check_payments', methods=['GET']) # Ruta de salud específica del blueprint
def health():
    """Ruta de salud para el blueprint de pagos."""
    current_app.logger.info("Ruta /v3/health_check_payments alcanzada.")
    return jsonify({"status": "OK", "message": "Servicio de Pagos Khipu (Blueprint) funcionando"}), 200

# Podrías añadir aquí otras rutas relacionadas con pagos de Khipu si las necesitas,
# como obtener estado de un pago, etc.
