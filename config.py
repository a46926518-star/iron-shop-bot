import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
BASE_URL = os.getenv("BASE_URL")
DJANGO_HOST = os.getenv("DJANGO_HOST")

if BASE_URL and not BASE_URL.endswith('/'):
    BASE_URL += '/'