import streamlit as st
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


def obtener_datos_rendimiento(servicio, dominio, fecha_inicio, fecha_fin):
    return servicio.searchanalytics().query(
        siteUrl=dominio,
        body={
            'startDate': fecha_inicio,
            'endDate': fecha_fin,
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


# Exportar los datos a un archivo CSV descargable
def exportar_a_csv(datos, dominio):
    df = pd.DataFrame(datos)
    nombre_archivo = f"scrapping_{dominio}.csv"
    df.to_csv(nombre_archivo, index=False)
    return nombre_archivo


# Interfaz de usuario con Streamlit
def main():
    # Título y descripción de la aplicación
    st.title("Análisis de rendimiento en Google Search Console")
    st.write("Esta aplicación realiza un análisis de rendimiento basado en datos de Google Search Console.")

    # Autenticación y obtención de datos
    servicio = autenticar()

    # Campo de entrada para el dominio
    dominio = st.text_input("Ingrese el dominio que desea consultar en Google Search Console (ejemplo: example.com)")

    # Selección de fechas
    st.header("Seleccione el rango de fechas")
    fecha_inicio = st.date_input("Fecha de inicio")
    fecha_fin = st.date_input("Fecha de fin")

    # Botón para obtener los datos
    if st.button("Obtener datos"):
        datos_rendimiento = obtener_datos_rendimiento(servicio, dominio, str(fecha_inicio), str(fecha_fin))
        archivo_csv = exportar_a_csv(datos_rendimiento['rows'], dominio)
        st.success("Datos obtenidos y exportados correctamente.")

        # Enlace para descargar el archivo CSV
        st.markdown(f"Descargar archivo CSV: [Descargar {archivo_csv}](./{archivo_csv})")

    # Información adicional
    st.header("Información adicional")
    st.write("Puedes encontrar los datos exportados en el archivo CSV descargable.")

if __name__ == "__main__":
    main()
