# openapi_server/__main__.py
import os
import sys 
import requests 
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging

log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
numeric_log_level = getattr(logging, log_level_str, logging.INFO)
logging.basicConfig(stream=sys.stdout, 
                    level=numeric_log_level,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.abspath(os.path.join(current_script_dir, '..'))
env_path_project_root = os.path.join(project_root_dir, '.env')

if os.path.exists(env_path_project_root):
    load_dotenv(dotenv_path=env_path_project_root, verbose=True)
    logging.info(f"Loaded .env file from: {os.path.abspath(env_path_project_root)}")
else:
    logging.info("No .env file found. Using system/container environment variables.")

app = Flask(__name__)

if app.debug:
    app.logger.setLevel(logging.DEBUG)
else:
    app.logger.setLevel(logging.INFO)

@app.route('/v3/payments', methods=['POST'])
def create_khipu_payment():
    if not request.is_json:
        app.logger.warning("Request body no es JSON")
        return jsonify({"error": "Request body debe ser JSON"}), 400

    client_request_data = request.get_json()
    app.logger.info(f"Solicitud POST /v3/payments recibida: {client_request_data}")

    khipu_merchant_api_key = os.environ.get('KHIPU_MERCHANT_API_KEY')
    khipu_target_base_url = os.environ.get('KHIPU_TARGET_API_URL', "https://payment-api.khipu.com")

    if not khipu_merchant_api_key:
        app.logger.error("KHIPU_MERCHANT_API_KEY no está configurada.")
        return jsonify({"error": "Error de configuración del servidor: clave API de Khipu faltante"}), 500

    subject = client_request_data.get("subject")
    amount_str = client_request_data.get("amount") 
    currency = client_request_data.get("currency")

    if not all([subject, amount_str, currency]):
        app.logger.warning(f"Faltan campos obligatorios. Recibido: subject='{subject}', amount='{amount_str}', currency='{currency}'")
        return jsonify({"error": "Faltan campos obligatorios: subject, amount, currency"}), 400
    
    # Validar que la moneda sea ARS (basado en el error de Khipu)
    # Para cumplir la consigna original de CLP, necesitarías una API Key para CLP.
    if currency != "ARS":
        app.logger.error(f"La API Key actual está configurada para ARS. Se recibió: {currency}")
        return jsonify({"error": "Moneda no válida para la API Key configurada. Usar ARS."}), 400

    try:
        amount = float(amount_str)
        if amount <= 0:
             app.logger.error(f"El monto debe ser mayor que cero, se recibió: {amount}")
             return jsonify({"error": "El monto debe ser mayor que cero"}), 400
        
        # El límite de $5.000 era para CLP. Para ARS, podrías definir otro límite o quitarlo para DemoBank.
        # Por ahora, lo comentaremos para ARS.
        # if currency == "ARS" and amount > XXXXX: # Define un límite si es necesario para ARS en DemoBank
        #      app.logger.warning(f"Monto {amount} ARS excede el límite de prueba. Ajustando...")
        #      amount = XXXXX.0 
    except ValueError:
        app.logger.error(f"El campo 'amount' no es un número válido: {amount_str}")
        return jsonify({"error": "El campo 'amount' debe ser un número válido"}), 400

    khipu_payload = {
        "subject": subject,
        "amount": amount, 
        "currency": currency, # ARS
        "transaction_id": client_request_data.get("transaction_id"),
        "custom": client_request_data.get("custom"),
        "body": client_request_data.get("body"),
        "payer_email": client_request_data.get("payer_email"),
        "return_url": client_request_data.get("return_url"),
        "cancel_url": client_request_data.get("cancel_url"),
        "notify_url": client_request_data.get("notify_url"), 
        "picture_url": client_request_data.get("picture_url"),
        "notify_api_version": client_request_data.get("notify_api_version", "1.3"),
        "expires_date": client_request_data.get("expires_date"),
    }
    khipu_payload_cleaned = {k: v for k, v in khipu_payload.items() if v is not None}
    
    khipu_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': khipu_merchant_api_key
    }

    khipu_actual_endpoint = f"{khipu_target_base_url.rstrip('/')}/v3/payments"
    
    app.logger.info(f"Enviando solicitud a Khipu: POST {khipu_actual_endpoint}")
    app.logger.debug(f"Khipu Payload (JSON a enviar): {khipu_payload_cleaned}")
    app.logger.debug(f"Khipu Headers (a enviar): {khipu_headers}")

    try:
        response_khipu = requests.post(
            khipu_actual_endpoint,
            json=khipu_payload_cleaned,
            headers=khipu_headers,
            timeout=30 
        )
        app.logger.info(f"Khipu raw response status: {response_khipu.status_code}")
        app.logger.debug(f"Khipu raw response headers: {response_khipu.headers}")
        app.logger.debug(f"Khipu raw response body: {response_khipu.text}")

        # Si Khipu devuelve un error (4xx o 5xx), propaga ese error.
        if not response_khipu.ok: # ok es True para códigos 2xx
            try:
                error_data = response_khipu.json()
                app.logger.error(f"Error de Khipu (JSON): {error_data}")
                # Devolver el error de Khipu directamente si es JSON
                return jsonify(error_data), response_khipu.status_code
            except ValueError: # Si el cuerpo del error no es JSON
                app.logger.error(f"Error de Khipu (texto plano): {response_khipu.text}")
                return jsonify({"error": "Error de Khipu", "details": response_khipu.text}), response_khipu.status_code
        
        khipu_response_data = response_khipu.json()
        app.logger.info(f"Respuesta JSON exitosa de Khipu: {khipu_response_data}")
        return jsonify(khipu_response_data), 201 # Pago creado exitosamente en Khipu

    except requests.exceptions.RequestException as e: # Errores de red, timeout, etc.
        app.logger.error(f"Error de conexión con Khipu: {str(e)}")
        return jsonify({"error": "Error de conexión al crear pago con Khipu", "details": str(e)}), 503
    except Exception as e: # Otros errores inesperados
        app.logger.error(f"Error inesperado en create_khipu_payment: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Servicio Khipu Wrapper (Flask Puro) funcionando"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    is_debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in ("true", "1", "t")
    
    if is_debug_mode:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)

    app.run(host='0.0.0.0', port=port, debug=is_debug_mode)
