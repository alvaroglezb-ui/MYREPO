# Imagen base
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiamos todo al contenedor
COPY . .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos el puerto 5000
EXPOSE 5000

# Ejecutamos la aplicación
CMD ["python", "app.py"]
