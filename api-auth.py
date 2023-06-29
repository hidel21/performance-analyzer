import google.auth
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Define las credenciales de la cuenta de servicio
service_account_info = {
  "type": "service_account",
  "project_id": "wearecontent-gsc",
  "private_key_id": "735e16b86d5227bf0ba502436f851a07aaa8986c",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCm2Kg9QlADUThG\nifGfP67OAKUn8+3V8xvLwn2cAGTMpEriDpnvYSQ1+Z/URkFE/e5yKhVICyxEvGA3\nISU4N6M91XuCnL9SOekq4G7aHi1lZDg+RT0gH/vkxDt6d5QdtlzanrWWeyEAU1E5\n61flTbRRKqBxDfRJYr9nTwHZLxeBsVXR5gWIWhjxFUWUZ1bbd4F/7nY5EXD7VCgr\noW+BQt15Kz/K9LAq/ES+2f/U0qZBAlgWlNXeE5qJJLRKMeluM6RtKgmG5E3VW8B0\nNfxmBl8B+cEgUY6rmwsIQgFWCjqpG9OMa7CCR1xSGaTeP2Tf5ub1fQ5aeFIV/TTg\n4/5BBUf5AgMBAAECggEAMK5ymD0q/2zJULubBm4cYPsLNVcVBCIE8DT1VXk/7/3X\n45GDFLdxS1Zkbhl5ndnBownoX7by2bNlF3DSXU7OkJIjkX6OzD0dbWdCsN2xPS46\nwuCM7zyl0J/5Asi1LN4yxY8dSKTwghnNT2r9oGhFvpEDczkxF+B6HHiO/4GgCDTu\nVhYdN4iNDpdyX6vfT2C5F1JNKGGxJwfkELSsw722U4GYbYH4k43KlNatPKWXo6u0\nK7fibUDrmFlS7r/vLL9s5TkC3i/GJj2o/f67IMnIPxUPa4rBtGgD8coSPUjP7FQF\nOXzbb+BBXTnKRXbvtDPCmZgnHCx/nky6MebhSrsiqQKBgQDqgCWptnALp2YX4yf8\nVMXyULXNZAmnKAqqKLr6swUY5/jidN0BqO5NeKVS04hRL/CZJNETHNFHW0PqoRhT\nyXVb4nQD49jY2GxCoicrnYfcRuV58hKqs3Gj52WcgGCZeP1K1UQJ/VKze4N6B5nS\nWaGwApP0f+cLJIlohS1S3voHFwKBgQC2JKD13SLjZU9POh7IExOog3Avcy58MZOC\n+8t5RYT9V3Fyy6Ggq+ZPRtTfTGJmSwwEnzBAvrKHiPSxBrH9ynY8RR92ZiYYE7lV\nxONYDyRzdQs/fO+y5rU4MZGOXziDlflLntd48A/ENa1xIkxJkqyw5JNbSeDUafbG\n8PIKmgaTbwKBgGFrHzpj+iQ9ROKDkeb36MwDz6Ml/gSdU+Dgzty7ZlC0febGGdJI\ntcclabkA+86OletpKhpAjIiSV6KvjgWw2bp0VzIOg9WCA2ejKZaq+Pf/0/FXKX4U\n0g7/YG0lv/vCEaf29S8ZODQsCbC2W6bRaaRPTdvzDq7IXPU47l1RGJm9AoGBAJD8\nESAEWYwWjY3sHqp1/PTrQzaSAdOcBuaBlZK/0r9yhnyxOMPTcW1zXWktvTndzQA0\n0s0GvseCLfxn7vCs43bQMt4lK3eI48MxCSKEUyiQZ1avFYIbgO7tDgb9JtgfXiRi\nmPPMa1BsxdXDTmRWG55nJCDLaurKOkRbcN8dgdSDAoGAMvaGl1DvFNSb9lUGeD/A\nO4gVDLLLPXnwV8QS4/6nnT/XMWGR1dm4C1LgaludVpdBx7CWyQhYY5TKsfOlm2r8\nHYazuzc4bgR4Yrxe7q/r/1TCDSyIUWJgc22xzS4fSf1v8AwJScPFvh+JB6XDG2Ob\n5Tt9fkTTF43UCIqTkkBeNok=\n-----END PRIVATE KEY-----\n",
  "client_email": "gsc-wac@wearecontent-gsc.iam.gserviceaccount.com",
  "client_id": "101654494016501081828",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gsc-wac%40wearecontent-gsc.iam.gserviceaccount.com"
}

# Load the service account credentials
#credentials = Credentials.from_service_account_info(service_account_info)

# Build the service
#webmasters_service = build('webmasters', 'v3', credentials=credentials)

# Use the service
#sites_list = webmasters_service.sites().list().execute()

#print(sites_list)


#Antes debes instalar las librerias ejecuta: pip install google-auth google-auth-oauthlib
