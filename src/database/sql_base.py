"""SQL database base class."""

import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import create_engine, Session

from src.utils.logger import get_logger

log = get_logger()


class SqlBase:
    """SQL database base/parent class."""

    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        """
        Initialize the SQL database base class.

        Args:
            host (str): The host of the SQL server.
            port (int): The port of the SQL server.
            user (str): The user of the SQL server.
            password (str): The password of the SQL server.
            db (str): The database of the SQL server.
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

        self.url = None

    def connect(self) -> None:
        """Connect to SQL server."""
        try:
            self.engine = create_engine(self.url)
            self.session = Session(self.engine)
            self.session.execute("SELECT 1")
            log.log(23, f"Connected to SQL: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            log.error(f"Error connecting to SQL: {e}")

    def disconnect(self) -> None:
        """Disconnect from SQL server."""
        try:
            self.engine.dispose()
            self.session.rollback()
            self.session.close()
            log.log(23, f"Disconnected from SQL: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            log.error(f"Error disconnecting from SQL: {e}")


class SqlBaseAsync:
    """Async SQL database base/parent class."""

    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        """
        Initialize the SQL database base class.

        Args:
            host (str): The host of the SQL server.
            port (int): The port of the SQL server.
            user (str): The user of the SQL server.
            password (str): The password of the SQL server.
            db (str): The database of the SQL server.
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

        self.url = None

    async def connect(self) -> None:
        """Connect to SQL server."""
        try:
            self.engine = create_async_engine(self.url)
            self.session = AsyncSession(self.engine)
            await self.session.execute("SELECT 1")
            log.log(23, f"Connected to SQL: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            log.error(f"Error connecting to SQL: {e}")

    async def disconnect(self) -> None:
        """Disconnect from SQL server."""
        try:
            await self.engine.dispose()
            await self.session.close()
            log.log(23, f"Disconnected from SQL: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            log.error(f"Error disconnecting from SQL: {e}")


if __name__ == "__main__":
    """Debugging."""
    import hydra
    from omegaconf import DictConfig

    