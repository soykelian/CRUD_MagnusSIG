import sys
from pathlib import Path

PROJECT_DIR = Path(r"C:\Users\Julian\Documents\CRUD_MagnusSIG")
sys.path.insert(0, str(PROJECT_DIR / "magnus_sig"))
from magnus_sig.settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": PROJECT_DIR / "tmp" / "manual_support" / "manual.sqlite3",
        "OPTIONS": {"timeout": 20},
    }
}
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
