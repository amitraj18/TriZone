"""
WSGI Production Entry Point for IRIS Backend
Usage:
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
    or
    waitress-serve --port=5000 wsgi:app
"""
import sys
from pathlib import Path

# Ensure backend directory is in python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

