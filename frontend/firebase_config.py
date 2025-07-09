import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()


firebase_config = {
    "apiKey": os.getenv('FIREBASE_API_KEY'),
    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
    "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),
    "projectId": os.getenv('FIREBASE_PROJECT_ID'),
    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    "appId": os.getenv('FIREBASE_APP_ID')
}


FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts"
API_KEY = os.getenv('FIREBASE_API_KEY')

class FirebaseAuth:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def create_user_with_email_and_password(self, email, password):
        url = f"{FIREBASE_AUTH_URL}:signUp?key={self.api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.json().get('error', {}).get('message', 'Unknown error'))
    
    def sign_in_with_email_and_password(self, email, password):
        url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={self.api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
            raise Exception(error_msg)
    
    def send_password_reset_email(self, email):
        url = f"{FIREBASE_AUTH_URL}:sendOobCode?key={self.api_key}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        response = requests.post(url, json=payload)
        return response.status_code == 200

class FirebaseDatabase:
    def __init__(self):
        pass


auth = FirebaseAuth(API_KEY)
database = FirebaseDatabase()
