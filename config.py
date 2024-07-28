import os

API_TOKEN = os.getenv('API_TOKEN')
REDIS_URL = os.getenv('REDIS_URL')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
POSTGRES_URL = os.getenv('POSTGRES_URL')