import os
import dotenv
from dotenv import load_dotenv

dotenv.load_dotenv()

# Environment Variables
api_token = os.getenv('TELEGRAM_BOT_API_KEY')
firebase_api_key = os.getenv('FIREBASE_API_KEY')