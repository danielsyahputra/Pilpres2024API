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
from typing import List, Union
from typing_extensions import Annotated
import src.utils.timer as t

from src.schema.database.article_schema import GoogleNews

class ListNewsRequest(BaseModel):
    query: str = Form(...)
    start_date: date = Form(...)
    end_date: date = Form(default=date.today())

    class Config:
        arbitrary_types_allowed = True


class ListNewsResponse(BaseModel):
    received_at: datetime = Field(datetime.now())
    result: List[GoogleNews] = Field([])
     
    class Config:
            arbitrary_types_allowed = True