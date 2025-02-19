Sistema de Recomendación de Películas

Este proyecto consiste en un sistema de recomendación de películas basado en similitud de títulos y popularidad, desarrollado con FastAPI y desplegado en Render.

📂 Datos Utilizados

Para este trabajo se utilizaron dos datasets:

credits.csv: Contiene información sobre el reparto y el equipo de producción de las películas.

movies.csv: Contiene información sobre las películas, incluyendo títulos, popularidad y fechas de lanzamiento.


Debido a las limitaciones del servidor utilizado para el despliegue, solo se usaron las primeras 500 filas de cada dataset.

🛠 Tecnologías Utilizadas

Python (pandas, scikit-learn, numpy, FastAPI)

TF-IDF Vectorizer y Similitud del Coseno para calcular similitudes
Scikit-Learn para procesamiento de datos

Render para el despliegue del modelo


🚀 Instalación y Uso

⿡ Clonar el repositorio

git clone https://github.com/tu_usuario/tu_repositorio.git
cd Proyecto MlOps

⿢ Crear y activar un entorno virtual

En Windows (Git Bash o PowerShell):
git clone https://(https://github.com/rook07/Sistema_Recomendacion)


⿢ Crear y activar un entorno virtual

En Windows (Git Bash o PowerShell):

python -m venv venv
source venv/Scripts/activate

En Mac/Linux:

python3 -m venv venv
source venv/bin/activate

⿣ Instalar dependencias

pip install -r requirements.txt

⿤ Ejecutar el servidor

uvicorn main:app --reload

📌 Uso de la API
El servicio cuenta con un endpoint principal:

/recomendacion?titulo=<nombre_pelicula>: Devuelve una lista de 5 películas similares basadas en la similitud de títulos y popularidad.


Ejemplo de consulta:

GET http://127.0.0.1:8000/recomendacion?titulo=Toy Story

🌍 Despliegue en Render

La API está desplegada en Render, permitiendo su acceso remoto.

URL de la API: https://tu-api-render.com

📜 Licencia

Este proyecto está bajo la licencia MIT. Puedes utilizarlo y modificarlo libremente.
📩 Para cualquier duda o sugerencia, contacta a ruizrocioay@egmail.com.





