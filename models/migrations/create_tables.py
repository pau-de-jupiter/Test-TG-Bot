import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

from config.config import settings

Base = declarative_base()

MIGRATION_SCRIPT = ["""
create table if not exists "Users"
(
    id         serial
    constraint "Users_pkey"
    primary key,
    login      varchar(255),
    username   varchar(255),
    tg_user_id bigint unique,
    status     varchar(10)               default 'Active',
    created_at timestamp with time zone default now()
); """,

"""create table if not exists public."Tasks"
(
    id               serial
    constraint "Tasks_pkey"
    primary key,
    name             varchar(255),
    description      text,
    tg_user_id       bigint,
    status           varchar(6)               default 'PROG',
    created_at       timestamp with time zone default now(),
    last_update      timestamp with time zone default now()::timestamp with time zone
);
"""]

async def run_migrations():
    engine = create_async_engine(settings.get_db_url(), echo=True)
    async with engine.begin() as conn:
        for script in MIGRATION_SCRIPT:
            await conn.execute(text(script))
            print("Migration applied successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migrations())
