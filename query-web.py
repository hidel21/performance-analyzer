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
import base64


nltk.download('stopwords')

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CREDENTIALS_FILE = 'client_secret_key.json'
URI_REDIRECCIONAMIENTO = [
    'http://localhost:8501/',
    'https://query-ana.streamlit.app/'
     ]



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


def obtener_datos_rendimiento(servicio, dominio, rango_fechas):
    return servicio.searchanalytics().query(
        siteUrl=dominio,
        body={
            'startDate': rango_fechas[0],
            'endDate': rango_fechas[1],
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
    if datos:
        df = pd.DataFrame(datos)
        nombre_archivo = f"scrapping_{dominio}.csv"
        
        archivo_csv = os.path.join(".", nombre_archivo)
        
        df.to_csv(archivo_csv, index=False)
        
        # Leer el archivo CSV como bytes
        with open(archivo_csv, "rb") as f:
            csv_bytes = f.read()
        
        # Generar el enlace de descarga
        b64 = base64.b64encode(csv_bytes).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{nombre_archivo}">Descargar CSV</a>'
        
        return href
    else:
        return None


def buscar_sitio(servicio):
    sitios = servicio.sites().list().execute()
    return sitios['siteEntry']


def main():
    # Título y descripción de la aplicación
    st.title("Análisis de rendimiento en Google Search Console")
    st.write("Esta aplicación realiza un análisis de rendimiento basado en datos de Google Search Console.")

    # Autenticación y obtención de datos
    servicio = autenticar()

    # Campo de búsqueda del sitio web
    st.header("Buscar sitio web")
    sitio_seleccionado = st.selectbox("Seleccione un sitio web", buscar_sitio(servicio))
    dominio = sitio_seleccionado['siteUrl']

    # Selección de fechas
    st.header("Seleccione el rango de fechas")
    fecha_inicio = st.date_input("Fecha de inicio")
    fecha_fin = st.date_input("Fecha de fin")

    archivo_csv = None  # Inicializar la variable con un valor predeterminado

       # Botón para obtener los datos
    if st.button("Obtener datos"):
        datos_rendimiento = obtener_datos_rendimiento(servicio, dominio, [str(fecha_inicio), str(fecha_fin)])

        if datos_rendimiento and 'rows' in datos_rendimiento:
            archivo_csv = exportar_a_csv(datos_rendimiento['rows'], dominio)
            st.success("Datos obtenidos correctamente.")
            
            if archivo_csv is not None:
                st.markdown(archivo_csv, unsafe_allow_html=True)
        else:
            st.error("No se encontraron datos en la respuesta de la API.")
    


if __name__ == "__main__":
    main()
