# -*- coding: utf-8 -*-

import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

CLIENT_SECRETS_FILE = "client_secret1.json"

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
API_SERVICE_NAME = 'searchconsole'
API_VERSION = 'v1'

app = flask.Flask(__name__)
app.secret_key = 'tester'


@app.route('/')
def index():
  return print_index_table()

@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
          **flask.session['credentials'])

    search_console_service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    site_list = search_console_service.sites().list().execute()

    verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry']
                        if s['permissionLevel'] != 'siteUnverifiedUser'
                        and s['siteUrl'].startswith('http')]

    results = '<!DOCTYPE html><html><body><table><tr><th>Verified site</th><th>Sitemaps</th></tr>'
    for site_url in verified_sites_urls:

        sitemaps = search_console_service.sitemaps().list(siteUrl=site_url).execute()
        results += '<tr><td>%s</td>' % (site_url)

        if 'sitemap' in sitemaps:
            sitemap_list = "<br />".join([s['path'] for s in sitemaps['sitemap']])
        else:
            sitemap_list = "<i>None</i>"
        results += '<td>%s</td></tr>' % (sitemap_list)

    results += '</table></body></html>'

    flask.session['credentials'] = credentials_to_dict(credentials)

    return results


@app.route('/authorize')
def authorize():
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      access_type='offline',
      include_granted_scopes='true')

  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '</td></tr></table>')


if __name__ == '__main__':
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  app.run('localhost', 8080, debug=True)