
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
df_actor =pd.read_csv('dataset_actor.csv')
df_director =pd.read_csv('dataset_director.csv')

# Crear una instancia de la aplicación FastAPI
app = FastAPI()

# Define el endpoint para contar las películas por mes
@app.get("/contar_peliculas_por_mes")
def contar_peliculas_por_mes(mes: str):
    """
    Este endpoint recibe un mes en idioma español y devuelve la cantidad de películas 
    estrenadas en ese mes según el dataset.
    """
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
    
    mes_numero = meses_dict.get(mes.lower())
    if mes_numero is None:
        return {"error": "Mes no válido. Por favor, ingresa un mes válido en español."}
    
    peliculas_estrenadas = df_cantidad[(df_cantidad['mes'] == mes_numero) & (df_cantidad['status'] == 'Released')]
    
    return {"mes": mes.capitalize(), "cantidad_peliculas": len(peliculas_estrenadas)}




@app.get("/cantidad_filmaciones_dia")
def cantidad_filmaciones_dia(dia: str):
    """Este endpoint recibe un día en idioma español y devuelve la cantidad de películas 
        estrenadas en ese día según el dataset."""
    dias_dict = {
        'domingo': 1,
        'lunes': 2,
        'martes': 3,
        'miercoles': 4,
        'jueves': 5,
        'viernes': 6,
        'sabado': 7
    }
    numero_dia = dias_dict.get(dia.lower())
    
    if numero_dia is None:
        return {"error": "Dia no válido. Por favor, ingresa un dia válido en español."}
    
    peliculas_estrenadas = df_cantidad[(df_cantidad['dia'] == numero_dia) & (df_cantidad['status'] == 'Released')]

    return {"dia": dia.capitalize(), "cantidad_peliculas": len(peliculas_estrenadas)}


@app.get("/votos_titulo")
def votos_titulo(titulo_de_la_filmacion: str):
    '''Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score.'''
    
    pelicula = df_votos[df_votos['title'].str.lower() == titulo_de_la_filmacion.lower()]
    
    if pelicula.empty:
        return "El título ingresado no se encuentra en la base de datos."
 
    titulo = pelicula['title'].iloc[0]
    cantidad_votos = int(pelicula['vote_count'].iloc[0])  # Conversión a int nativo
    promedio_votos = float(pelicula['vote_average'].iloc[0])
    
    if cantidad_votos < 2000:
       return {
            "mensaje": f"La película '{titulo}' no cumple con el requisito mínimo de 2000 valoraciones (tiene {cantidad_votos} valoraciones)."
        }
       
    return {
        "titulo": titulo,
        "cantidad_votos": cantidad_votos,
        "promedio_votos": round(promedio_votos, 2)
    }



@app.get("/score_titulo")
def score_titulo(titulo_de_la_filmacion: str):
    '''Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score.'''

    pelicula = df_score[df_score['title'].str.lower() == titulo_de_la_filmacion.lower()]
    
    if pelicula.empty: #si es incorrecto o vacio )
     return {"error": "El título ingresado no se encuentra en la base de datos."}
 
    titulo = pelicula['title'].iloc[0]
    anio_estreno = pelicula['release_year'].iloc[0]
    score = pelicula['popularity'].iloc[0]
    
    return {
        "titulo": titulo,
        "anio_estreno": anio_estreno,
        "score": score,
        "mensaje": f"La película '{titulo}' fue estrenada en el año {anio_estreno} con un score/popularidad de {score}."
    }
    
    
    
@app.get("/actor")
def actor(nombre_actor: str):
    nombre_actor = nombre_actor.lower()
    if not df_actor['cast_name'].str.lower().isin([nombre_actor]).any():
        return f"Error: El actor '{nombre_actor}' no se encuentra en la base de datos."

    actor = df_actor[df_actor['cast_name'].str.lower() == nombre_actor]
    director = df_director[df_director['name'] == nombre_actor]
    if not director.empty:
        return f"Error: El actor '{nombre_actor}' también es director en algunas películas. No se incluirán en el análisis."

    total_peliculas = len(actor)
    total_retorno = actor['return'].sum()
    exito= total_retorno / total_peliculas if total_peliculas > 0 else 0
    
    return f"El actor {nombre_actor} ha participado en {total_peliculas} filmaciones, logrando un retorno total de {total_retorno:.2f} con un promedio de {exito:.2f} por filmación."


@app.get("/director")
def get_director(nombre_director):
    
    nombre_director = nombre_director.lower()
    director= df_director[df_director['name'].str.lower() == nombre_director]
    
    if director.empty:
        return f"Error: El director '{nombre_director.title()}' no se encuentra en la base de datos."
    
    pelicula_id = director['id'].tolist()
    peliculas = df_actor[df_actor['id'].isin(pelicula_id)][['id', 'title', 'release_date', 'budget', 'revenue', 'return']].drop_duplicates(subset=['id'])
    if peliculas.empty:
        return f"Error: No se encontraron películas dirigidas por '{nombre_director.title()}'."
    exito= peliculas['return'].sum()
    cant_peliculas = len(peliculas)

    mensaje = f" El director {nombre_director.title()} ha dirigido {cant_peliculas} películas, con un exito de {exito:.2f}.\n\n"
    mensaje += " **Listado de películas:**\n"

    for _, row in peliculas.iterrows():
        mensaje += (f"- {row['title']} (estrenada en: {row['release_date'].strftime('%Y-%m-%d')}): "
                    f"Retorno: {row['return']:.2f}, Costo: {row['budget']}, Ganancia: {row['revenue']}\n")

    return mensaje


# "SISTEMA DE RECOMENDACION"

vec_tfidf = TfidfVectorizer(stop_words='english')
matriz_tfidf = vec_tfidf.fit_transform(df_recomendacion['titulos'])
similitud_coseno = cosine_similarity(matriz_tfidf, matriz_tfidf)
indices = pd.Series(df_recomendacion.index, index=df_recomendacion['titulos']).drop_duplicates()

@app.get("/recomendacion")
def recomendacion(titulo: str):
    ''' 
    Recibe el título de una película y devuelve una lista de 5 películas similares.
    '''
    titulo = titulo.lower()
    if titulo not in indices:
        return {"error": "El título ingresado no se encuentra en la base de datos."}

    idx = indices[titulo]
    # Calcula las similitudes de los títulos
    sim_scores = list(enumerate(similitud_coseno[idx]))
    
    # Ordenar las películas por su puntuación de similitud de títulos
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # Excluir la película original y limitar a las 10 más similares
    sim_scores = sim_scores[1:11]
    
    # Crear una métrica combinada basada en popularidad y similitud
    recomendaciones = []
    for i, sim in sim_scores:
        score = sim * 0.7 + df_recomendacion.iloc[i]['popularidad'] * 0.3
        recomendaciones.append((df_recomendacion.iloc[i]['titulos'], score))
    
    recomendaciones = sorted(recomendaciones, key=lambda x: x[1], reverse=True)[:5]
    
    # Extraer los títulos de las películas recomendadas
    recomendacion_titulos = [r[0] for r in recomendaciones]
    
    return {"recomendaciones": recomendacion_titulos}






