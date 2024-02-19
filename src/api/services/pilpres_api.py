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
from datetime import datetime, date, timedelta
from pathlib import Path
import src.utils.exceptions as exceptions
import src.utils.timer as t
import time

from src.schema.auth.auth_schema import CurrentUser, Token
from src.database.mongodb_base import MongodbBase
from src.utils.auth import Authentication
from src.utils.logger import get_logger
from src.api.base_api import BaseAPI
from fastapi.middleware.cors import CORSMiddleware
from newspaper import Article as ArticleNews
from newspaper.article import ArticleException

from src.schema.database.article_schema import (
    GoogleNews,
    Article,
    Sentiment
)
from newspaper import Config
from src.schema.services.pilpres_api import *
from src.utils.services.fetch_news import fetch_related_news

import warnings
warnings.filterwarnings("ignore")  

import nltk
from gnews import GNews
from datetime import datetime, date, timedelta
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

log = get_logger()

class PilpresAPI(BaseAPI):
    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg
        self.app = app
        self.router = APIRouter()
        self.auth = Authentication(**self.cfg.api.auth.bearer)

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        self.config = Config()
        self.config.browser_user_agent = user_agent

        self.google_news = GNews(language="id", country="ID")
        self.pretrained= "mdhugol/indonesia-bert-sentiment-classification"
        self.model = AutoModelForSequenceClassification.from_pretrained(self.pretrained)
        self.tokenizer = AutoTokenizer.from_pretrained(self.pretrained)
        self.sentiment_analyzer = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
        self.label = {'LABEL_0': 'positive', 'LABEL_1': 'neutral', 'LABEL_2': 'negative'}

        # engine
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

            news_result = await self.fetch_related_news(query=form.query, 
                                                        limit_per_day=form.limit_per_day,
                                                        start_date=form.start_date,
                                                        end_date=form.end_date)
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
    
    async def get_sentimen_from_news(self, text):
        result = self.sentiment_analyzer(text)
        sentimen = self.label[result[0]['label']]
        return sentimen

    async def fetch_related_news(self, query: str,
                                    limit_per_day: int, 
                                    start_date: date,
                                    end_date: date):
        scrapped_news = []
        self.google_news.max_results = limit_per_day
        while start_date < end_date:
            self.google_news.start_date = (start_date.year, start_date.month, start_date.day)
            self.google_news.period = "1d"

            news_result = self.google_news.get_news(key=query)
            for news in news_result:
                try:
                    article_result = ArticleNews(url=news['url'])
                    article_result.build()
                    article_dict = {
                        "title": article_result.title,
                        "text": article_result.text,
                        "summary": article_result.summary,
                        "publish_date": article_result.publish_date,
                        "keywords": article_result.keywords
                    }
                    sentimen = await self.get_sentimen_from_news(article_dict['summary'])
                    article = Article(**article_dict, sentiment=Sentiment[sentimen])
                    news_obj = GoogleNews(**news, article=article)
                    await news_obj.insert()

                    scrapped_news.append(news_obj)
                except AttributeError as e:
                    log.error(str(e))
                except ArticleException as ae:
                    pass
            start_date += timedelta(days=1)
        return scrapped_news