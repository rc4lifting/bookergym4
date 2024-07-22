import os
import dotenv

dotenv.load_dotenv('.env')

# Environment Variables
api_token = os.getenv('TELEGRAM_BOT_API_KEY')

google_cloud_project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')

firebase_api_key = os.getenv('FIREBASE_API_KEY')
firebase_database_url = os.getenv('FIREBASE_DATABASE_URL')
firebase_private_key_id = os.getenv('FIREBASE_PRIVATE_KEY_ID')
firebase_private_key = os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n')
firebase_client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
firebase_client_id = os.getenv('FIREBASE_CLIENT_ID')
firebase_client_x509_cert_url = os.getenv("FIREBASE_CLIENT_X509_CERT_URL")

schedule_gsheet_id = os.getenv('SCHEDULE_GSHEET_ID')
schedule_private_key_id = os.getenv('SCHEDULE_PRIVATE_KEY_ID')
schedule_private_key = os.getenv('SCHEDULE_PRIVATE_KEY').replace('\\n', '\n')
schedule_client_email = os.getenv('SCHEDULE_CLIENT_EMAIL')
schedule_client_id = os.getenv('SCHEDULE_CLIENT_ID')
schedule_client_x509_cert_url = os.getenv("SCHEDULE_CLIENT_X509_CERT_URL")

utownfbs_username = os.getenv('UTOWNFBS_USERNAME')
utownfbs_password = os.getenv('UTOWNFBS_PASSWORD')


# Firebase Service Account Config
firebase_config = {
  "type": "service_account",
  "project_id": google_cloud_project_id,
  "private_key_id": firebase_private_key_id,
  "private_key": firebase_private_key,
  "client_email": firebase_client_email,
  "client_id": firebase_client_id,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": firebase_client_x509_cert_url,
  "universe_domain": "googleapis.com"
}

# Google Sheet Service Account Config
schedule_credentials = {
  "type": "service_account",
  "project_id": google_cloud_project_id,
  "private_key_id": schedule_private_key_id,
  "private_key": schedule_private_key,
  "client_email": schedule_client_email,
  "client_id": schedule_client_id,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": schedule_client_x509_cert_url,
  "universe_domain": "googleapis.com"
}

#UTownFBS Portal Login
utownfbs_login = {
  "username": utownfbs_username,
  "password": utownfbs_password
}

# Email sending 
resend_api_key = os.environ["RESEND_API_KEY"]