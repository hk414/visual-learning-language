import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

cred = os.getenv("FIREBASE_CREDENTIALS_PATH")

firebase_admin.initialize_app(cred)

db = firestore.client()

def test_firebase():
    doc_ref = db.collection("test_collection2").document("test_doc")
    doc_ref.set({"message": "Firebase is working!"})
    print("Data stored successfully!")

test_firebase()
