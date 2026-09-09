"""Production WSGI entry point, e.g. `gunicorn wsgi:app`."""
import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app(os.getenv("FLASK_CONFIG", "production"))
