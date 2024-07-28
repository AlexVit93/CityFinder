import asyncpg

class Database:
    def __init__(self, dsn):
        self.dsn = dsn

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn)
        await self.create_table()

    async def create_table(self):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS cities (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_city_name ON cities(name);
            ''')

    async def add_city(self, city):
        async with self.pool.acquire() as connection:
            await connection.execute('INSERT INTO cities (name) VALUES ($1) ON CONFLICT DO NOTHING', city)

    async def get_nearest_city(self, city):
        async with self.pool.acquire() as connection:
            result = await connection.fetch('SELECT name FROM cities WHERE name != $1 LIMIT 1', city)
            return result[0]['name'] if result else None