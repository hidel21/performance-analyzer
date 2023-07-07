import pandas as pd
import pickle
import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from io import BytesIO



nltk.download('stopwords')

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CREDENTIALS_FILE = 'client_secret_key.json'
URI_REDIRECCIONAMIENTO = 'http://localhost:55875/'

def guardar_credenciales(credenciales):
    with open('credenciales.pickle', 'wb') as f:
        pickle.dump(credenciales, f)

def cargar_credenciales():
    try:
        with open('credenciales.pickle', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

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

def obtener_datos_rendimiento(servicio, start_date, end_date, url):
    return servicio.searchanalytics().query(
        siteUrl=url,
        body={
            'startDate': start_date,
            'endDate': end_date,
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
    stop_words = set(stopwords.words('spanish'))
    palabras_clave = [word for word in url.split('/') if word.lower() not in stop_words]
    return palabras_clave

def exportar_consulta_base(datos_rendimiento):
    # Obtener los datos de la consulta base
    filas = datos_rendimiento['rows']
    datos_base = pd.DataFrame(filas)  # Convertir 'filas' en un DataFrame

    # Guarda el DataFrame a un archivo de Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        datos_base.to_excel(writer)
    output.seek(0)

def main():
    st.title("Análisis de rendimiento de página web")
    st.write(""" ## Autenticación ## """)

    if "servicio" not in st.session_state or st.button("Autenticar"):
        st.session_state.servicio = autenticar()
        st.success('Autenticación realizada exitosamente!')

    st.write(""" ## Obtención de Datos de Rendimiento ## """)

    # Los valores por defecto han sido sustituidos por otras fechas y una URL diferente
    start_date = st.date_input('Fecha de inicio', value=pd.to_datetime('2023-01-01'))
    end_date = st.date_input('Fecha de fin', value=pd.to_datetime('2023-06-30'))
    url = st.text_input('Ingresa la URL del sitio web', value='https://www.example.com')

    if "datos_rendimiento" not in st.session_state or st.button("Obtener Datos"):
        st.session_state.datos_rendimiento = obtener_datos_rendimiento(st.session_state.servicio, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), url)
        st.success('Datos de rendimiento obtenidos exitosamente!')

    st.write(""" ## Exportar Consulta Base ## """)

    if st.button("Exportar Consulta"):
        output = exportar_consulta_base(st.session_state.datos_rendimiento)
        st.success('Consulta base exportada exitosamente!')

        # Crea un botón de descarga para el archivo de Excel
        st.download_button(
            label="Descargar archivo de Excel",
            data=output,
            file_name='consulta_base.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
    main()
