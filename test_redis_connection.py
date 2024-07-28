import os
import redis.asyncio as redis
import asyncio

async def test_redis_connection():
    REDIS_HOST = os.getenv('REDISHOST')
    REDIS_PORT = int(os.getenv('REDISPORT', 6379))
    REDIS_PASSWORD = os.getenv('REDISPASSWORD')

    print(f"REDIS_HOST={REDIS_HOST}, REDIS_PORT={REDIS_PORT}, REDIS_PASSWORD={'yes' if REDIS_PASSWORD else 'no'}")

    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD
        )

        response = await client.ping()
        print(f"PING response: {response}")

        if response:
            print("Successfully connected to Redis")
        else:
            print("Failed to connect to Redis")
    except Exception as e:
        print(f"Error connecting to Redis: {e}")

if __name__ == "__main__":
    asyncio.run(test_redis_connection())
