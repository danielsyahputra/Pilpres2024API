import nltk
from gnews import GNews
from datetime import datetime, date, timedelta
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from src.schema.database.article_schema import (
    GoogleNews,
    Article,
    Sentiment
)
from src.utils.logger import get_logger
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from newspaper import Config


import warnings
warnings.filterwarnings("ignore")    


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
config = Config()
config.browser_user_agent = user_agent

log = get_logger()

client = AsyncIOMotorClient("mongodb://alfabeta:alfabeta123@pilpres_analyzer_mongo:4242")

google_news = GNews(language="id", country="ID")
pretrained= "mdhugol/indonesia-bert-sentiment-classification"
model = AutoModelForSequenceClassification.from_pretrained(pretrained)
tokenizer = AutoTokenizer.from_pretrained(pretrained)
sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
label = {'LABEL_0': 'positive', 'LABEL_1': 'neutral', 'LABEL_2': 'negative'}

async def get_sentimen_from_news(text):
    result = sentiment_analyzer(text)
    sentimen = label[result[0]['label']]
    return sentimen

async def fetch_related_news(query: str,
                                limit_per_day: int, 
                                start_date: date,
                                end_date: date):

    await init_beanie(database=client['pilpres'], document_models=[GoogleNews])

    scrapped_news = []
    google_news.max_results = limit_per_day
    while start_date < end_date:
        google_news.start_date = (start_date.year, start_date.month, start_date.day)
        google_news.period = "1d"

        news_result = google_news.get_news(key=query)
        for news in news_result:
            try:
                article_result = google_news.get_full_article(url=news['url'])
                article_result.parse()
                article_result.nlp()
                article_dict = {
                    "title": article_result.title,
                    "text": article_result.text,
                    "summary": article_result.summary,
                    "publish_date": article_result.publish_date,
                    "keywords": article_result.keywords
                }
                sentimen = await get_sentimen_from_news(article_dict['summary'])
                article = Article(**article_dict, sentiment=Sentiment[sentimen])
                news_obj = GoogleNews(**news, article=article)
                await news_obj.insert()

                scrapped_news.append(news_obj)
            except AttributeError as e:
                log.error(str(e))
        start_date += timedelta(days=1)
    return scrapped_news