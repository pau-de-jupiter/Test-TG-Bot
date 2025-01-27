
from models.migrations.create_tables import run_migrations

async def main():
    await run_migrations()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())