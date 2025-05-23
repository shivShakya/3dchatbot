from firebase_admin import credentials, initialize_app, firestore, get_app

def initialize_firebase():
    try:
        get_app()
    except ValueError:
        cred = credentials.Certificate("keys.json")
        initialize_app(cred)

initialize_firebase()
db = firestore.client()
