from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
STATICFILES_DIRS = [BASE_DIR / 'static']
ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', 'localhost', '192.168.1.60']