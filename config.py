import os

API_TOKEN = os.getenv('API_TOKEN')
REDIS_URL = os.getenv('REDIS_URL')
POSTGRES_URL = os.getenv('POSTGRES_URL')

print(f"REDIS_URL={REDIS_URL}, POSTGRES_URL={POSTGRES_URL}")
