# app/services/khipu_service.py
import os
import requests
import logging

# Obtener el logger configurado por la fábrica de la aplicación
# Es mejor obtener el logger específico del módulo actual.
logger = logging.getLogger(__name__) 
# Si __name__ es 'app.services.khipu_service', usará la configuración raíz si no hay una específica.

# Constantes
DEFAULT_KHIPU_TARGET_API_URL = "https://payment-api.khipu.com"
DEFAULT_NOTIFY_API_VERSION = "1.3"
REQUEST_TIMEOUT_SECONDS = 30

class KhipuServiceError(Exception):
    """Excepción base para errores del servicio Khipu."""
    def __init__(self, message, status_code=None, khipu_response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.khipu_response_data = khipu_response_data

class KhipuConfigError(KhipuServiceError):
    """Error si la configuración de Khipu (ej. API Key) falta."""
    pass

class KhipuRequestError(KhipuServiceError):
    """Error durante la solicitud a la API de Khipu (ej. HTTPError)."""
    pass

class KhipuConnectionError(KhipuServiceError):
    """Error de conexión con la API de Khipu."""
    pass


def _prepare_khipu_payload(client_data: dict) -> dict:
    """
    Prepara y valida el payload para enviar a la API de Khipu.
    Aplica lógica de negocio como validación de moneda y monto.
    """
    subject = client_data.get("subject")
    amount_str = client_data.get("amount")
    currency = client_data.get("currency")

    if not all([subject, amount_str, currency]):
        logger.warning(f"Faltan campos obligatorios para Khipu. Recibido: subject='{subject}', amount='{amount_str}', currency='{currency}'")
        raise KhipuServiceError("Faltan campos obligatorios: subject, amount, currency", status_code=400)

    # La consigna actual es ARS para tu API Key
    if currency != "ARS": 
        logger.error(f"Moneda debe ser ARS para la API Key configurada. Se recibió: {currency}")
        raise KhipuServiceError("Moneda no válida para la API Key configurada. Usar ARS.", status_code=400)

    try:
        amount = float(amount_str)
        if amount <= 0:
            logger.error(f"El monto debe ser mayor que cero, se recibió: {amount}")
            raise KhipuServiceError("El monto debe ser mayor que cero", status_code=400)
        
        # Límite para ARS en DemoBank (si aplica, ajustar o quitar)
        # Ejemplo: si el límite fuera 100000 ARS
        # if currency == "ARS" and amount > 100000: 
        #     logger.warning(f"Monto {amount} ARS excede el límite de prueba de 100000 ARS. Ajustando...")
        #     amount = 100000.0
    except ValueError:
        logger.error(f"El campo 'amount' no es un número válido: {amount_str}")
        raise KhipuServiceError("El campo 'amount' debe ser un número válido", status_code=400)

    payload = {
        "subject": subject,
        "amount": amount,
        "currency": currency,
        "transaction_id": client_data.get("transaction_id"),
        "custom": client_data.get("custom"),
        "body": client_data.get("body"),
        "payer_email": client_data.get("payer_email"),
        "return_url": client_data.get("return_url"),
        "cancel_url": client_data.get("cancel_url"),
        "notify_url": client_data.get("notify_url"),
        "picture_url": client_data.get("picture_url"),
        "notify_api_version": client_data.get("notify_api_version", DEFAULT_NOTIFY_API_VERSION),
        "expires_date": client_data.get("expires_date"),
    }
    return {k: v for k, v in payload.items() if v is not None}


def create_payment_intent(client_payment_data: dict) -> dict:
    """
    Crea una intención de pago en Khipu.

    :param client_payment_data: Diccionario con los datos del pago del cliente.
    :return: Diccionario con la respuesta de Khipu si es exitosa.
    :raises KhipuConfigError: Si falta la API Key.
    :raises KhipuRequestError: Si Khipu devuelve un error HTTP.
    :raises KhipuConnectionError: Si hay un problema de red.
    :raises KhipuServiceError: Para otros errores de validación o inesperados.
    """
    khipu_merchant_api_key = os.environ.get('KHIPU_MERCHANT_API_KEY')
    khipu_target_base_url = os.environ.get('KHIPU_TARGET_API_URL', DEFAULT_KHIPU_TARGET_API_URL)

    if not khipu_merchant_api_key:
        logger.error("KHIPU_MERCHANT_API_KEY no está configurada.")
        raise KhipuConfigError("Error de configuración del servidor: clave API de Khipu faltante", status_code=500)

    try:
        # Validar y preparar el payload antes de enviarlo
        khipu_payload = _prepare_khipu_payload(client_payment_data)
    except KhipuServiceError as e: # Re-lanzar errores de validación de _prepare_khipu_payload
        raise e

    khipu_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': khipu_merchant_api_key
    }

    khipu_api_endpoint = f"{khipu_target_base_url.rstrip('/')}/v3/payments"
    
    logger.info(f"Enviando solicitud a Khipu API: POST {khipu_api_endpoint}")
    logger.debug(f"Khipu Payload (JSON a enviar): {khipu_payload}")
    logger.debug(f"Khipu Headers (a enviar): {khipu_headers}")

    try:
        response = requests.post(
            khipu_api_endpoint,
            json=khipu_payload,
            headers=khipu_headers,
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        logger.info(f"Khipu raw response status: {response.status_code}")
        logger.debug(f"Khipu raw response headers: {response.headers}")
        logger.debug(f"Khipu raw response body (text): {response.text}")

        if not response.ok: # Si el código de estado no es 2xx
            try:
                error_data = response.json()
                error_message = error_data.get("message", response.text)
                # Intentar extraer un mensaje más específico si Khipu lo provee
                if "errors" in error_data and isinstance(error_data["errors"], list) and len(error_data["errors"]) > 0:
                     error_detail = error_data['errors'][0]
                     error_message = f"Campo '{error_detail.get('field', 'desconocido')}': {error_detail.get('message', response.text)}"
                logger.error(f"Error HTTP de Khipu: {response.status_code} - Detalle: {error_message} - Respuesta Completa: {response.text}")
                raise KhipuRequestError(f"Error de Khipu: {error_message}", status_code=response.status_code, khipu_response_data=error_data)
            except ValueError: # Si el cuerpo del error no es JSON
                logger.error(f"Error HTTP de Khipu (texto plano): {response.status_code} - {response.text}")
                raise KhipuRequestError(f"Error de Khipu: {response.text}", status_code=response.status_code, khipu_response_data=response.text)
        
        # Si la respuesta es OK (2xx)
        khipu_response_data = response.json()
        logger.info(f"Respuesta JSON exitosa de Khipu: {khipu_response_data}")
        return khipu_response_data

    except requests.exceptions.Timeout:
        logger.error(f"Timeout al conectar con Khipu API: {khipu_api_endpoint}")
        raise KhipuConnectionError("Timeout al conectar con Khipu API", status_code=504)
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error de conexión con Khipu API: {str(e)}")
        raise KhipuConnectionError(f"Error de conexión con Khipu API: {str(e)}", status_code=503)
    except requests.exceptions.RequestException as e: 
        logger.error(f"Error general de requests al llamar a Khipu API: {str(e)}")
        raise KhipuServiceError(f"Error al comunicarse con Khipu: {str(e)}", status_code=502)
    except Exception as e: 
        logger.error(f"Error inesperado al crear intención de pago en Khipu: {str(e)}", exc_info=True)
        raise KhipuServiceError(f"Error interno inesperado: {str(e)}", status_code=500)

