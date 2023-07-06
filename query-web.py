import pandas as pd
import pickle
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

nltk.download('stopwords')

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CREDENTIALS_FILE = 'client_secret_key.json'
URI_REDIRECCIONAMIENTO = 'http://localhost:55875/'
VIEW_ID = 'https://pintuco.com.co/'


# Función para guardar las credenciales en un archivo pickle
def guardar_credenciales(credenciales):
    with open('credenciales.pickle', 'wb') as f:
        pickle.dump(credenciales, f)


# Función para cargar las credenciales desde un archivo pickle
def cargar_credenciales():
    try:
        with open('credenciales.pickle', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


# Función para autenticar o cargar las credenciales
def autenticar():
    credenciales = cargar_credenciales()

    if credenciales:
        return build('webmasters', 'v3', credentials=credenciales)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES,
                                                         redirect_uri=URI_REDIRECCIONAMIENTO)
        credenciales = flow.run_local_server(port=55875)
        guardar_credenciales(credenciales)
        return build('webmasters', 'v3', credentials=credenciales)


def obtener_datos_rendimiento(servicio):
    return servicio.searchanalytics().query(
        siteUrl=VIEW_ID,
        body={
            'startDate': '2022-02-19',
            'endDate': '2023-05-30',
            'dimensions': ['page'],
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'contains',
                    'expression': '/blog/'
                }]
            }],
            'metrics': ['clicks', 'impressions', 'ctr', 'position'],
            'rowLimit': 3000
        }
    ).execute()


def obtener_palabras_clave(url):
    # Eliminar stopwords
    stop_words = set(stopwords.words('spanish'))

    # Obtener las palabras clave de la URL
    palabras_clave = [word for word in url.split('/') if word.lower() not in stop_words]

    return palabras_clave


# Exportar primero la consulta
def exportar_consulta_base(datos_rendimiento):
    # Obtener los datos de la consulta base
    filas = datos_rendimiento['rows']
    datos_base = []
    urls = []

    for fila in filas:
        url = fila['keys'][0]
        clicks = fila['clicks']
        impressions = fila['impressions']
        urls.append(url)
        datos_base.append({'URL': url, 'Clicks': clicks, 'Impressions': impressions})

    # Crear DataFrame con los datos de la consulta base
    df = pd.DataFrame(datos_base)

    # Realizar la extracción de frases clave y análisis de similitud de texto
    vectorizer = TfidfVectorizer()
    matriz_tfidf = vectorizer.fit_transform(urls)
    similitud = cosine_similarity(matriz_tfidf)

    # Agregar las frases clave y sumar las métricas de los conjuntos similares
    conjuntos = {}
    for i, url in enumerate(urls):
        palabras_clave = obtener_palabras_clave(url)
        conjunto_similar = None

        # Buscar el conjunto similar en los conjuntos existentes
        for conjunto, urls_conjunto in conjuntos.items():
            urls_similares = [u for u in urls if u in urls_conjunto]
            similitud_maxima = similitud[i, [urls.index(u) for u in urls_conjunto]].max()

            if similitud_maxima > 0.6:  # Ajusta este valor según tus necesidades
                conjunto_similar = conjunto
                break

        if conjunto_similar:
            # Si se encontró un conjunto similar, agregar la URL al conjunto
            conjuntos[conjunto_similar].append(url)
            df.loc[i, 'Frase clave'] = conjunto_similar
        else:
            # Si no se encontró un conjunto similar, crear uno nuevo
            conjunto_nuevo = ' '.join(palabras_clave)
            conjuntos[conjunto_nuevo] = [url]
            df.loc[i, 'Frase clave'] = conjunto_nuevo

    # Crear un nuevo DataFrame con los conjuntos y sus métricas
    conjuntos_datos = []
    for conjunto, urls_conjunto in conjuntos.items():
        clicks_suma = df.loc[df['URL'].isin(urls_conjunto), 'Clicks'].sum()
        impressions_suma = df.loc[df['URL'].isin(urls_conjunto), 'Impressions'].sum()
        conjuntos_datos.append({'Frase clave': conjunto, 'Clicks': clicks_suma, 'Impressions': impressions_suma})

    df_conjuntos = pd.DataFrame(conjuntos_datos)

    # Reemplazar los espacios por "/" en los datos de la columna "Frase clave"
    df_conjuntos['Frase clave'] = df_conjuntos['Frase clave'].str.replace(' ', '/')

    # Guardar el DataFrame de los conjuntos en un archivo Excel
    df_conjuntos.to_excel('consulta-base.xlsx', index=False)


servicio = autenticar()
datos_rendimiento = obtener_datos_rendimiento(servicio)
exportar_consulta_base(datos_rendimiento)
