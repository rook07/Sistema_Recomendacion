#!/bin/bash

# Crear el entorno virtual (si no existe)
if [ ! -d "venv" ]; then
  python -m venv venv
fi

# Activar el entorno virtual (ruta correcta en Windows)
source venv/Scripts/activate

# Instalar las dependencias (DENTRO del entorno virtual activado)
pip install -r requirements.txt

# Ejecutar la aplicación (DENTRO del entorno virtual activado)
uvicorn main:app --host 0.0.0.0 --port:10000 # Usa la variable de entorno $PORT
