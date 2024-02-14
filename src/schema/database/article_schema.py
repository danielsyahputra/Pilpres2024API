import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

from datetime import datetime

from beanie import Document
from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, List, Optional

import src.utils.timer as t

class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    unknown = "unknown"

class Article(BaseModel):
    title: str = Field(...)
    text: str = Field(...)
    summary: str = Field(...)
    keywords: List[str] = Field(None)
    sentiment: Sentiment = Field(Sentiment.unknown)

class GoogleNews(Document):
    title: str = Field(...)
    description: Optional[str] = Field(None)
    published_date: Optional[datetime] = Field(None)
    url: Optional[str] = Field(None)
    publisher: Optional[Any] = Field(None)
    article: Article = Field(...)

    class Config:
        arbitrary_types_allowed = True