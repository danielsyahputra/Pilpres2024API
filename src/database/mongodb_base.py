"""MongoDB base module."""

import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from schema.user.user_schema import User
from src.utils.logger import get_logger

log = get_logger()


class MongodbBase:
    """Mongodb base/parent class."""

    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        """
        Initialize the mongodb base class.

        Args:
            host (str): The host of the mongodb server.
            port (int): The port of the mongodb server.
            user (str): The user of the mongodb server.
            password (str): The password of the mongodb server.
            db (str): The database of the mongodb server.
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

    async def connect(self) -> None:
        """Connect to mongodb server."""
        try:
            self.client = AsyncIOMotorClient(
                f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}",
                serverSelectionTimeoutMS=1000,
            )
            self.client.server_info()
            await init_beanie(
                database=self.client[self.db],
                document_models=[
                    User,
                ],
            )
            log.log(22, f"Connected to mongodb: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            log.error(f"Error connecting to mongodb: {e}")

    async def disconnect(self) -> None:
        """Disconnect from mongodb server."""
        try:
            self.client.close()
            log.log(22, f"Disconnected from mongodb: {self.host}:{self.port}/{self.db}")
        except Exception as e:
            log.error(f"Error disconnecting from mongodb: {e}")