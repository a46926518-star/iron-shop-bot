import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID") or 0)

DJANGO_HOST = (os.getenv("DJANGO_HOST") or "https://iron-shop.onrender.com").rstrip("/")

BASE_URL = f"{DJANGO_HOST}/api"
MEDIA_URL = f"{DJANGO_HOST}/media"