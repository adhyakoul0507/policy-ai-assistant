import firebase_admin

from firebase_admin import credentials, firestore

import os

from dotenv import load_dotenv

load_dotenv()

if not firebase_admin._apps:

   

    if os.getenv('RENDER') or os.getenv('FIREBASE_PRIVATE_KEY'):

        

        firebase_credentials = {

            "type": "service_account",

            "project_id": os.getenv('FIREBASE_PROJECT_ID'),

            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),

            "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n') if os.getenv('FIREBASE_PRIVATE_KEY') else None,

            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),

            "client_id": os.getenv('FIREBASE_CLIENT_ID'),

            "auth_uri": "https://accounts.google.com/o/oauth2/auth",

            "token_uri": "https://oauth2.googleapis.com/token",

            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",

            "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL')

        }

        cred = credentials.Certificate(firebase_credentials)

    else:

        

        try:

            cred = credentials.Certificate('../firebase/serviceAccountKey.json')

        except FileNotFoundError:

            cred = credentials.Certificate('firebase/serviceAccountKey.json')

    

    firebase_admin.initialize_app(cred)

db = firestore.client()

firebase_config = {

    "apiKey": os.getenv('FIREBASE_API_KEY'),

    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),

    "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),

    "projectId": os.getenv('FIREBASE_PROJECT_ID'),

    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),

    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),

    "appId": os.getenv('FIREBASE_APP_ID')

}
