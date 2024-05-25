import os
import dotenv
from dotenv import load_dotenv

dotenv.load_dotenv()

# Environment Variables
api_token = os.getenv('TELEGRAM_BOT_API_KEY')
firebase_api_key = os.getenv('FIREBASE_API_KEY')
firebase_project_id = os.getenv('FIREBASE_PROJECT_ID')
firebase_database_url = os.getenv('FIREBASE_DATABASE_URL')
firebase_private_key_id = os.getenv('FIREBASE_PRIVATE_KEY_ID')
firebase_private_key = os.getenv('FIREBASE_PRIVATE_KEY').replace("\\n", '\n')
firebase_client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
firebase_client_id = os.getenv('FIREBASE_CLIENT_ID')

# Firebase Config
firebase_config = {
  "type": "service_account",
  "project_id": firebase_project_id,
  "private_key_id": firebase_private_key_id,
  "private_key": firebase_private_key,
  "client_email": firebase_client_email,
  "client_id": firebase_client_id,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-r5xf7%40bookergym4-dfd9f.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
