"""Main module for the application."""

import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

import hydra
from omegaconf import DictConfig

from src.utils.logger import get_logger
from contextlib import asynccontextmanager


log = get_logger()

def main_api(cfg: DictConfig) -> None:
    """Main function for the API."""
    import asyncio
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    from src.api.runner import GunicornRunner
    from src.database.mongodb_base import MongodbBase
    from src.api.base_api import BaseAPI

    from src.api.services.pilpres_api import PilpresAPI
    
    log.info(f"Starting API server at {cfg.api.host}:{cfg.api.port}...")
    
    mongodb = MongodbBase(**cfg.database.mongodb)
    @asynccontextmanager
    async def lifespan(app: FastAPI):  # type: ignore
        await mongodb.connect()
        print("Startup complete")
        yield
        await mongodb.disconnect()
        print("Shutdown complete")
    
    # API service
    base_api = BaseAPI(cfg, mongodb)
    pilpres_api = PilpresAPI(cfg)
    
    app = FastAPI(
        title=f"Pilpres 2024 Sentiment Analysis REST API",
        description=f"Pilpres 2024 Sentiment Analysis REST API",
        version="0.1.1",
        docs_url="/", 
        redoc_url="/docs",
        lifespan=lifespan,
        
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.api.middleware.cors.allow_origins,
        allow_credentials=cfg.api.middleware.cors.allow_credentials,
        allow_methods=cfg.api.middleware.cors.allow_methods,
        allow_headers=cfg.api.middleware.cors.allow_headers,
    )
    
    app.include_router(base_api.router)
    app.include_router(pilpres_api.router)
    
    # setup runner
    runner = GunicornRunner(
        app,
        host=cfg.api.host,
        port=cfg.api.port,
        workers=cfg.api.workers,
        log_level=cfg.logger.level,
    )
    runner.run()
