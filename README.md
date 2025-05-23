# Integración de Pagos Khipu con Flask (Argentina - ARS)

Este proyecto es una aplicación Flask que demuestra la integración con la API de pagos de Khipu, permitiendo la creación de intenciones de pago a través de llamadas a la API. Está configurado para operar con el entorno DemoBank de Khipu, específicamente para el mercado argentino (ARS).

## Características Principales

* **Creación de Pagos Vía API:** Implementa el endpoint `/v3/payments` para generar cobros en Khipu.
* **Flask Puro:** Utiliza Flask sin capas adicionales como Connexion para un control directo.
* **Estructura Modular:** Código organizado en Blueprints para rutas y una capa de servicios para la lógica de Khipu.
* **Configuración por Variables de Entorno:** Manejo seguro de credenciales y configuraciones.
* **Listo para Docker:** Incluye un `Dockerfile` para facilitar la contenerización y el despliegue.
* **Logging Detallado:** Configuración de logging para depuración y seguimiento.

## Prerrequisitos

* Python 3.9+
* Podman (o Docker)
* Una cuenta en Khipu DemoBank con una API Key (formato UUID) habilitada para ARS.
* `pip` para la gestión de paquetes Python.

# Credenciales y configuración de Khipu
KHIPU_MERCHANT_API_KEY="TU_API_KEY_DE_KHIPU_FORMATO_UUID_PARA_ARS"
KHIPU_TARGET_API_URL="[https://payment-api.khipu.com](https://payment-api.khipu.com)" # URL de la API v3 de Khipu

# Configuración de Flask
FLASK_DEBUG="1"         # 1 para activar el modo debug, 0 para desactivar
FLASK_RUN_HOST="0.0.0.0"
FLASK_RUN_PORT="8000"

# Nivel de Logging para la aplicación (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL="DEBUG"

Importante: Reemplaza "TU_API_KEY_DE_KHIPU_FORMATO_UUID_PARA_ARS" con tu API Key real de Khipu DemoBank para ARS.


## Instalación y Ejecución
Ejecución con Docker/Podman

    Construir la Imagen:
    Desde la raíz del proyecto (donde está el Dockerfile):

    podman build -t khipu-app:latest .
    # o si usas Docker:
    # docker build -t khipu-app:latest .

    Ejecutar el Contenedor:
    Puedes pasar las variables de entorno usando la opción --env-file o múltiples opciones -e.

    podman run -p 8000:8000 --env-file .env khipu-app:latest
    # o
    # podman run -p 8000:8000 \
    #   -e KHIPU_MERCHANT_API_KEY="TU_API_KEY_DE_KHIPU" \
    #   -e KHIPU_TARGET_API_URL="[https://payment-api.khipu.com](https://payment-api.khipu.com)" \
    #   -e FLASK_DEBUG="1" \
    #   -e LOG_LEVEL="DEBUG" \
    #   -e FLASK_RUN_PORT="8000" \
    #   khipu-app:latest

    La aplicación estará disponible en http://localhost:8000. Si mapeas a un puerto diferente en el host (ej. -p 8001:8000), accede a través de ese puerto (ej. http://localhost:8001).

Endpoints de la API
1. Crear un Pago

    Método: POST

    URL: /v3/payments

    Headers:

        Content-Type: application/json

    Cuerpo (Body - JSON):

    {
      "subject": "Pago de Prueba ARS",
      "amount": "150.75", 
      "currency": "ARS",
      "transaction_id": "TX-MIAPP-12345",
      "payer_email": "comprador.prueba@example.com",
      "return_url": "[https://mi-aplicacion.com/pago/retorno](https://mi-aplicacion.com/pago/retorno)",
      "cancel_url": "[https://mi-aplicacion.com/pago/cancelado](https://mi-aplicacion.com/pago/cancelado)",
      "notify_url": "[https://mi-webhook-publico.com/khipu/notificacion](https://mi-webhook-publico.com/khipu/notificacion)"
    }

    Campos Opcionales Adicionales: body, bank_id, payer_name, picture_url, notify_api_version, expires_date, custom, etc. (ver _prepare_khipu_payload en khipu_service.py para más detalles).

    Respuesta Exitosa (201 Created):
    Un JSON con los detalles del pago creado por Khipu, incluyendo payment_id y payment_url.

    {
        "payment_id": "IDENTIFICADOR_DE_PAGO_DE_KHIPU",
        "payment_url": "URL_DE_KHIPU_PARA_PAGAR_AL_USUARIO",
        "simplified_transfer_url": "...",
        "transfer_url": "...",
        "app_url": "...",
        "ready_for_terminal": false
    }

2. Chequeo de Salud del Blueprint de Pagos

    Método: GET

    URL: /v3/health_check_payments

    Respuesta Exitosa (200 OK):

    {
        "status": "OK",
        "message": "Servicio de Pagos Khipu (Blueprint) funcionando"
    }

Pruebas

Se recomienda usar una herramienta como Postman o curl para probar los endpoints.

Ejemplo con curl para crear un pago:

curl -X POST http://localhost:8000/v3/payments \
-H "Content-Type: application/json" \
-d '{
  "subject": "Pago de Prueba ARS con cURL",
  "amount": "250.50",
  "currency": "ARS",
  "transaction_id": "TX-CURL-001",
  "payer_email": "curl_user@example.com",
  "return_url": "[https://example.com/curl/return](https://example.com/curl/return)",
  "cancel_url": "[https://example.com/curl/cancel](https://example.com/curl/cancel)",
  "notify_url": "[https://tu-ngrok-o-webhook-publico.com/khipu_notify](https://tu-ngrok-o-webhook-publico.com/khipu_notify)"
}'

Próximos Pasos y Mejoras Potenciales

    Implementar un endpoint para recibir y verificar las notificaciones webhook de Khipu.

    Añadir validación de datos más robusta para el cuerpo de las solicitudes (ej. usando Pydantic o Marshmallow).

    Expandir la capa de servicios para manejar otros endpoints de la API de Khipu (ej. obtener estado de un pago, reembolsos).

    Implementar tests unitarios y de integración.

    Configurar un servidor WSGI de producción (
