import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

from bson import ObjectId
from datetime import datetime, date
from beanie import Document
from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, dataclasses
from typing import Any
from enum import Enum
from typing import List, Union, Optional
from typing_extensions import Annotated
import src.utils.timer as t

from src.schema.database.article_schema import GoogleNews

__all__ = [
    "FetchNewsRequest",
    "FetchNewsResponse",
    "GetListNewsRequest",
    "GetListNewsResponse",
    "GetNewsDetailsRequest",
    "GetNewsDetailsResponse",
    "NewsResult"
]

class FetchNewsRequest(BaseModel):
    query: str = Form(...)
    limit_per_day: int = Form(default=20)
    start_date: date = Form(...)
    end_date: date = Form(default=date.today())

    class Config:
        arbitrary_types_allowed = True

class NewsResult(GoogleNews):
    id: str = Field(...)

class FetchNewsResponse(BaseModel):
    received_at: datetime = Field(datetime.now())
    result: List[NewsResult] = Field([])
     
    class Config:
        arbitrary_types_allowed = True

class GetListNewsRequest(BaseModel):
    start_date: date = Form(...)
    end_date: date = Form(default=None)

    class Config:
        arbitrary_types_allowed = True

class GetListNewsResponse(BaseModel):
    received_at: datetime = Field(datetime.now())
    result: List[NewsResult] = Field([])

    class Config:
        arbitrary_types_allowed = True

class GetNewsDetailsRequest(BaseModel):
    news_id: str = Form(...)

    class Config:
        arbitrary_types_allowed = True

class GetNewsDetailsResponse(BaseModel):
    received_at: datetime = Field(datetime.now())
    result: GoogleNews = Field(None)

    class Config:
        arbitrary_types_allowed = True