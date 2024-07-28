import os

API_TOKEN = os.getenv('API_TOKEN')
REDIS_HOST = os.getenv('REDISHOST')
REDIS_PASSWORD = os.getenv('REDISPASSWORD')
REDIS_PORT = int(os.getenv('REDISPORT', 6379))
REDIS_USER = os.getenv('REDISUSER')
POSTGRES_URL = os.getenv('POSTGRES_URL')
