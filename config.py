import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DJANGO_HOST = os.getenv("DJANGO_HOST", "https://iron-shop.onrender.com/").rstrip("/")

BASE_URL = f"{DJANGO_HOST}/api/"
MEDIA_URL = f"{DJANGO_HOST}/media/"