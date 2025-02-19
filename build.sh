#!/bin/bash

# Crear el entorno virtual si no existe
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activar el entorno virtual (ajustado para Linux/macOS en Render)
source venv/bin/activate

# Instalar las dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar la aplicación en Render
uvicorn main:app --host 0.0.0.0 --port 10000

