"""Local development entry point: `python run.py`."""
import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app(os.getenv("FLASK_CONFIG", "development"))

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
