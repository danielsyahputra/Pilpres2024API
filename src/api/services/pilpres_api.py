import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

from fastapi import APIRouter, Depends, FastAPI, Request

from omegaconf import DictConfig

import os
from datetime import datetime
from pathlib import Path
import src.utils.exceptions as exceptions
import src.utils.timer as t
import time

from src.schema.auth.auth_schema import CurrentUser, Token
from src.database.mongodb_base import MongodbBase
from src.utils.auth import Authentication
from src.utils.logger import get_logger
from src.api.base_api import BaseAPI

from src.schema.database.article_schema import GoogleNews
from src.schema.services.pilpres_api import (
    ListNewsRequest,
    ListNewsResponse
)

app = FastAPI()

log = get_logger()

class PilpresAPI(BaseAPI):
    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg
        self.app = app
        self.router = APIRouter()
        self.auth = Authentication(**self.cfg.api.auth.bearer)
        self.setup()

    def setup(self) -> None:
        "Setup routes"

        @self.router.post(
            "/api/news/fetch",
            tags=["Google News"],
            description="Fetch Google News Based on Keyword",
            dependencies=[Depends(self.bearer_auth)]
        )
        async def get_list_of_news(
            request: Request,
            form: ListNewsRequest = Depends(),
            current_user: CurrentUser = Depends(self.bearer_auth)
        ):
            log.log(25, f"List news request from: {current_user.username} - {request.client.host}",)

            news_result = await GoogleNews.find_all().to_list()
            response = ListNewsResponse(received_at=datetime.now(), result=news_result)
            return response