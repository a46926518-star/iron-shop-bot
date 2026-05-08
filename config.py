import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8701385504:AAGATjB5tyQNdoifS-VaOJ8pNRb7DwFRRzg")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! .env ni tekshir")

ADMIN_ID = int(os.getenv("8549599284") or 0)

DJANGO_HOST = (os.getenv("DJANGO_HOST") or "http://127.0.0.1:8001").rstrip("/")

BASE_URL = f"{DJANGO_HOST}/api"
MEDIA_URL = f"{DJANGO_HOST}/media"

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")