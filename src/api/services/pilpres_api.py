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
from bson import ObjectId
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
from src.schema.services.pilpres_api import *

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
        async def fetch_news(
            request: Request,
            form: FetchNewsRequest = Depends(),
            current_user: CurrentUser = Depends(self.bearer_auth)
        ):
            log.log(25, f"Fetch news request from: {current_user.username} - {request.client.host}")

            print(form)
            print(form.query, print(type(form.query)))
            print(form.start_date, print(type(form.start_date)))

            news_result = await GoogleNews.find_all().to_list()
            news_result = [NewsResult(id=str(news.id),
                                      title=news.title,
                                      description=news.description,
                                      published_date=news.published_date,
                                      url=news.url,
                                      publisher=news.publisher,
                                      article=news.article) for news in news_result]
            response = FetchNewsResponse(received_at=datetime.now(), result=news_result)
            return response
        
        @self.router.get(
            "/api/news/list",
            tags=["Google News"],
            description="Get List of Google News",
            dependencies=[Depends(self.bearer_auth)]
        )
        async def get_list_of_news(
            request: Request,
            current_user: CurrentUser = Depends(self.bearer_auth)
        ):
            log.log(25, f"Get list of news request from: {current_user.username} - {request.client.host}")
            news_result = await GoogleNews.find_all().to_list()
            news_result = [NewsResult(id=str(news.id),
                                      title=news.title,
                                      description=news.description,
                                      published_date=news.published_date,
                                      url=news.url,
                                      publisher=news.publisher,
                                      article=news.article) for news in news_result]
            response = GetListNewsResponse(received_at=datetime.now(), result=news_result)
            return response      
        
        @self.router.get(
            "/api/news",
            tags=["Google News"],
            description="Get News Detail",
            dependencies=[Depends(self.bearer_auth)]
        )
        async def get_news_detail(
            request: Request,
            form: GetNewsDetailsRequest = Depends(),
            current_user: CurrentUser = Depends(self.bearer_auth)
        ):
            log.log(25, f"Get news detail request from: {current_user.username} - {request.client.host}")
            news = await GoogleNews.find_one(
                    GoogleNews.id == ObjectId(form.news_id)
                )
            return GetNewsDetailsResponse(
                received_at=datetime.now(),
                result=NewsResult(id=str(news.id),
                                title=news.title,
                                description=news.description,
                                published_date=news.published_date,
                                url=news.url,
                                publisher=news.publisher,
                                article=news.article)
            )