
import pandas as pd
import numpy as np
from fastapi import FastAPI
from json import JSONDecodeError
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Carga de datasets
df_cantidad = pd.read_csv('dataset_cantidad.csv')
df_score = pd.read_csv('dataset_score_title.csv')
df_votos = pd.read_csv('dataset_votos.csv')
df_recomendacion = pd.read_csv('dataset_recomendacion.csv')


# Crear una instancia de la aplicación FastAPI
app = FastAPI()

# Define el endpoint para contar las películas por mes
@app.get("/contar_peliculas_por_mes")
def contar_peliculas_por_mes(mes: str):
    """
    Este endpoint recibe un mes en idioma español y devuelve la cantidad de películas 
    estrenadas en ese mes según el dataset.
    """
    # Diccionario para mapear nombres de meses a números
    meses_dict = {
        'enero': 1,
        'febrero': 2,
        'marzo': 3,
        'abril': 4,
        'mayo': 5,
        'junio': 6,
        'julio': 7,
        'agosto': 8,
        'septiembre': 9,
        'octubre': 10,
        'noviembre': 11,
        'diciembre': 12
    }
    
    # Convertir el nombre del mes a minúsculas y buscar en el diccionario
    mes_numero = meses_dict.get(mes.lower())
    
    # Verificar si el mes es válido
    if mes_numero is None:
        return {"error": "Mes no válido. Por favor, ingresa un mes válido en español."}
    
    # Filtrar el DataFrame para contar las películas estrenadas en el mes dado
    peliculas_estrenadas = df_cantidad[(df_cantidad['mes'] == mes_numero) & (df_cantidad['status'] == 'Released')]
    
    # Retornar la cantidad de películas
    return {"mes": mes.capitalize(), "cantidad_peliculas": len(peliculas_estrenadas)}




@app.get("/cantidad_filmaciones_dia")
def cantidad_filmaciones_dia(dia: str):
    """Este endpoint recibe un día en idioma español y devuelve la cantidad de películas 
        estrenadas en ese día según el dataset."""
    # Diccionario para mapear nombres de dias a números
    dias_dict = {
        'domingo': 1,
        'lunes': 2,
        'martes': 3,
        'miercoles': 4,
        'jueves': 5,
        'viernes': 6,
        'sabado': 7
    }
    
    # Convertir el nombre del dia a minúsculas y buscar en el diccionario
    numero_dia = dias_dict.get(dia.lower())
    
    if numero_dia is None:
        return {"error": "Dia no válido. Por favor, ingresa un dia válido en español."}
    
    # Filtrar el DataFrame para contar las películas estrenadas en el dia dado
    peliculas_estrenadas = df_cantidad[(df_cantidad['dia'] == numero_dia) & (df_cantidad['status'] == 'Released')]

    # Retornar la cantidad de películas
    return {"dia": dia.capitalize(), "cantidad_peliculas": len(peliculas_estrenadas)}

@app.get("/votos_titulo")
def votos_titulo(titulo_de_la_filmacion: str):
    '''Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score.'''
    # Filtrar el DataFrame para encontrar el título ingresado
    pelicula = df_votos[df_votos['title'].str.lower() == titulo_de_la_filmacion.lower()]
    
    if pelicula.empty:
        return "El título ingresado no se encuentra en la base de datos."
    
    # Extraer información de la 
    titulo = int(pelicula['title'].iloc[0])
    cantidad_votos = int(pelicula['vote_count'].iloc[0])  # Conversión a int nativo
    promedio_votos = float(pelicula['vote_average'].iloc[0])
    
    # Verificar si cumple con la condición de al menos 2000 valoraciones
    if cantidad_votos < 2000:
       return {
            "mensaje": f"La película '{titulo}' no cumple con el requisito mínimo de 2000 valoraciones (tiene {cantidad_votos} valoraciones)."
        }
    # Retornar la información si cumple la condición
    return {
        "titulo": titulo,
        "cantidad_votos": cantidad_votos,
        "promedio_votos": round(promedio_votos, 2)
    }



@app.get("/score_titulo")
def score_titulo(titulo_de_la_filmacion: str):
    '''Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score.'''
    # Filtra el DataFrame para encontrar la fila correspondiente al título ingresado
    pelicula = df_score[df_score['title'].str.lower() == titulo_de_la_filmacion.lower()]
    
    if pelicula.empty: #si es incorrecto o vacio )
     return {"error": "El título ingresado no se encuentra en la base de datos."}
      
    # Extrae los valores y los almacena en un df llamado pelicula y lee la unica fila 
    titulo = pelicula['title'].iloc[0]
    anio_estreno = pelicula['release_year'].iloc[0]
    score = pelicula['popularity'].iloc[0]
    
    return {
        "titulo": titulo,
        "anio_estreno": anio_estreno,
        "score": score,
        "mensaje": f"La película '{titulo}' fue estrenada en el año {anio_estreno} con un score/popularidad de {score}."
    }
    
    

# Reviso los valores nulos
df_recomendacion['titulo'] = df_recomendacion['title'].fillna('')
df_recomendacion['popularidad'] = df_recomendacion['popularity'].fillna(0)

# Normalizar la popularidad para combinar similitudes
df_recomendacion['popularidad_normalizada'] = (
    df_recomendacion['popularidad'] - df_recomendacion['popularidad'].min()
) / (df_recomendacion['popularidad'].max() - df_recomendacion['popularidad'].min())

# Convertir los títulos del dataset a minúsculas para consistencia
df_recomendacion['titulo_normalizado'] = df_recomendacion['titulo'].str.lower()

# Crear un vectorizador TF-IDF para calcular similitud de títulos normalizados
vectorizador_tfidf = TfidfVectorizer(stop_words='english')
matriz_tfidf = vectorizador_tfidf.fit_transform(df_recomendacion['titulo_normalizado'])

# Calcular la matriz de similitud del coseno para los títulos
similitud_coseno = cosine_similarity(matriz_tfidf, matriz_tfidf)

# Crear una serie para mapear títulos normalizados a índices
indices_titulos = pd.Series(df_recomendacion.index, index=df_recomendacion['titulo_normalizado']).drop_duplicates()

@app.get("/recomendacion")
def recomendacion(titulo: str):
    """
    Recibe el título de una película y devuelve una lista de 5 películas similares.
    """
    # Normalizar el título ingresado a minúsculas
    titulo_normalizado = titulo.lower()
    
    # Verificar si el título existe en los datos
    if titulo_normalizado not in indices_titulos:
        return {"error": "El título ingresado no se encuentra en la base de datos."}

    # Obtener el índice de la película
    indice = indices_titulos[titulo_normalizado]
    
    # Calcular las similitudes de los títulos
    puntajes_similitud = list(enumerate(similitud_coseno[indice]))
    
    # Ordenar las películas por su puntuación de similitud de títulos
    puntajes_similitud = sorted(puntajes_similitud, key=lambda x: x[1], reverse=True)
    
    # Excluir la película original y limitar a las 10 más similares
    puntajes_similitud = puntajes_similitud[1:11]
    
    # Crear una métrica combinada basada en popularidad y similitud
    recomendaciones = []
    for i, similitud in puntajes_similitud:
        puntaje = similitud * 0.7 + df_recomendacion.iloc[i]['popularidad_normalizada'] * 0.3
        recomendaciones.append((df_recomendacion.iloc[i]['titulo'], puntaje))
    
    # Ordenar por el puntaje combinado
    recomendaciones = sorted(recomendaciones, key=lambda x: x[1], reverse=True)[:5]
    
    # Extraer los títulos de las películas recomendadas
    titulos_recomendados = [r[0] for r in recomendaciones]
    
    return {"recomendaciones": titulos_recomendados}






