# Usar una versión específica de Python (ej. 3.9, 3.11 o la que estés usando)
FROM python:3.12-alpine 

# Establecer variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crear directorio de la aplicación
WORKDIR /usr/src/app

# Instalar dependencias
# Copiar requirements.txt primero para aprovechar el caché de Docker
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
# Asumiendo que tu Dockerfile está en khipu_integration_project/
# y la app está en khipu_integration_project/app/
COPY ./app ./app
COPY run.py .
# Si tienes otros archivos en la raíz como config.py, cópialos también.
# COPY config.py . 

# Exponer el puerto que la aplicación usará
EXPOSE 8000

# Comando para ejecutar la aplicación
# Usaremos 'python run.py' para el servidor de desarrollo de Flask.
# Para producción, se recomienda un servidor WSGI como Gunicorn:
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:application"]
CMD ["python", "run.py"]
