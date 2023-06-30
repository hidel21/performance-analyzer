import  os
from flask import Flask, jsonify, redirect, request
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

CLIENT_SECRETS_FILE = "client_secret1.json"
API_SERVICE_NAME = 'searchconsole'
API_VERSION = 'v1'

app = Flask(__name__)
app.secret_key = 'tester'

@app.route('/')
def index():
    return '''
    <h1>API de Google Search Console</h1>
    <p>¡Bienvenido! Utiliza la ruta /performance/sitio_web para obtener datos de rendimiento de un sitio web específico.</p>
    '''

@app.route('/performance/<sitio_web>')
def obtener_datos_rendimiento(sitio_web):
    if 'credentials' not in request.session:
        return redirect('/authorize')

    cred = credentials.Credentials(**request.session['credentials'])

    search_console_service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)

    request_body = {
        'startDate': 'yyyy-mm-dd',  # Fecha de inicio para la consulta
        'endDate': 'yyyy-mm-dd',    # Fecha de fin para la consulta
        'dimensions': ['date'],     # Dimensiones para la consulta (por ejemplo, fecha)
        'searchType': 'web',        # Tipo de búsqueda (web, image, video, etc.)
        'rowLimit': 10              # Límite de filas de resultados
    }

    response = search_console_service.searchanalytics().query(
        siteUrl='https://pintuco.com.co/', body=request_body).execute()

    return jsonify(response)

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
    flow.redirect_uri = request.url_root + 'oauth2callback'
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    request.session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = request.session['state']
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=['https://www.googleapis.com/auth/webmasters.readonly'], state=state)
    flow.redirect_uri = request.url_root + 'oauth2callback'
    flow.fetch_token(authorization_response=request.url)
    cred = flow.credentials
    request.session['credentials'] = credentials_to_dict(cred)
    return redirect('/')

def credentials_to_dict(credentials):
    return {
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
         }

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080, debug=True)