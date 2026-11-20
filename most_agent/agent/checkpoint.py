
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from most_agent.db.session import SessionFactory


def get_checkpoint_database_url() -> str:
    """Reuse the database connection configuration from SQLAlchemy."""

    engine = SessionFactory.kw["bind"]

    # SQLAlchemy uses postgresql+psycopg.
    # Psycopg's connection URI uses postgresql.
    database_url = engine.url.set(
        drivername="postgresql"
    )

    return database_url.render_as_string(
        hide_password=False
    )


@asynccontextmanager
async def open_postgres_checkpointer(
) -> AsyncIterator[AsyncPostgresSaver]:
    """Manage the PostgreSQL checkpointer connection."""

    database_url = get_checkpoint_database_url()

    async with AsyncPostgresSaver.from_conn_string(
        database_url
    ) as checkpointer:

        await checkpointer.setup()

        yield checkpointer
