import os
from .base import *


DEBUG = False
ALLOWED_HOSTS = ['*']

HOST = os.getenv('HOST')
BASE_URL: str = f'https://{HOST}'
if not HOST:
    raise ValueError('Please set the HOST environment variable')