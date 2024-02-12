"""Gunicorn runner for the API."""

import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

import uvicorn
from gunicorn.app import base

from src.utils.logger import get_logger

log = get_logger()


class GunicornApp(base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


class GunicornRunner:
    def __init__(self, app, host, port, workers, log_level):
        self.app = app
        self.host = host
        self.port = port
        self.workers = workers
        self.log_level = log_level

    def run(self):
        log.info(f"Starting gunicorn server on {self.host}:{self.port}...")
        options = {
            "bind": f"{self.host}:{self.port}",
            "workers": self.workers,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "loglevel": self.log_level,
            "timeout": 120,
        }
        GunicornApp(self.app, options).run()


class UvicornRunner:
    def __init__(self, app, host, port, log_level):
        self.app = app
        self.host = host
        self.port = port
        self.log_level = log_level

    def run(self):
        log.info(f"Starting uvicorn server on {self.host}:{self.port}...")
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level=self.log_level,
        )