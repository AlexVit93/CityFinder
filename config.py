import os

API_TOKEN = os.getenv('API_TOKEN')
REDIS_HOST = "redis.railway.internal"
REDIS_PORT = 6379  
REDIS_PASSWORD = "JvtKAapimpWMwQastKNsGqSutkWggzjb"  
POSTGRES_URL = os.getenv('POSTGRES_URL')

print(f"REDIS_HOST={REDIS_HOST}, REDIS_PORT={REDIS_PORT}, REDIS_PASSWORD={'yes' if REDIS_PASSWORD else 'no'}, POSTGRES_URL={POSTGRES_URL}")
