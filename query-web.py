import pandas as pd
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CREDENTIALS_FILE = 'client_secret_key.json'
URI_REDIRECCIONAMIENTO = 'http://localhost:55875/'
VIEW_ID = 'https://pintuco.com.co/'


def autenticar():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES, redirect_uri=URI_REDIRECCIONAMIENTO)
    credenciales = flow.run_local_server(port=55875)
    return build('webmasters', 'v3', credentials=credenciales)

def obtener_datos_rendimiento(servicio):
    return servicio.searchanalytics().query(
        siteUrl= VIEW_ID,
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

servicio = autenticar()
datos_rendimiento = obtener_datos_rendimiento(servicio)

# Exportar primero la consulta
def exportar_consulta_base(datos_rendimiento):
    # Obtener los datos de la consulta base
    filas = datos_rendimiento['rows']
    datos_base = []
    for fila in filas:
        url = fila['keys'][0]
        clicks = fila['clicks']
        impressions = fila['impressions']
        datos_base.append({'URL': url, 'Clicks': clicks, 'Impressions': impressions})

    # Crear DataFrame con los datos de la consulta base
    df = pd.DataFrame(datos_base)

    # Guardar el DataFrame en un archivo Excel
    df.to_excel('consulta-base.xlsx', index=False)

datos_rendimiento = obtener_datos_rendimiento(servicio)
exportar_consulta_base(datos_rendimiento) 

# Obtener la lista de filas desde el resultado
filas = datos_rendimiento['rows']

# Paso adicional: Procesamiento y agrupación de datos
datos_agrupados = {}
for fila in filas:
    url = fila['keys'][0]
    clicks = fila['clicks']
    impressions = fila['impressions']
    palabras_clave = url.split('/blog/')[1].split('/')  # Obtener palabras clave después de "blog/" en la URL
    clave = '-'.join(palabras_clave)
    if clave not in datos_agrupados:
        datos_agrupados[clave] = {'url': url, 'clicks': 0, 'impressions': 0}
    datos_agrupados[clave]['clicks'] += clicks
    datos_agrupados[clave]['impressions'] += impressions

# Crear lista de datos finales para el DataFrame
datos_finales = []
for conjunto in datos_agrupados.values():
    datos_finales.append(conjunto)

# Crear DataFrame con los datos finales
df = pd.DataFrame(datos_finales, columns=['url', 'clicks', 'impressions'])

# Guardar el DataFrame en un archivo Excel
df.to_excel('resultados.xlsx', index=False)