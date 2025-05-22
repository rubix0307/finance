import os
from .base import *


DEBUG = False
ALLOWED_HOSTS = ['*']

HOST = os.getenv('HOST', 'localhost')
BASE_URL: str = f'https://{HOST}'

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]