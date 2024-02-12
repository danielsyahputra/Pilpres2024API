"""Main module for the application."""

import pyrootutils

ROOT = pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git"],
    pythonpath=True,
    dotenv=True,
)

import asyncio

import hydra
from omegaconf import DictConfig

from src.utils.logger import get_logger
from src.api.main_api import main_api
log = get_logger()


if __name__ == "__main__":

    @hydra.main(config_path=f"{ROOT}/configs", config_name="main", version_base=None)
    def main(cfg: DictConfig) -> None:
        """Main function."""
        if cfg.mode == "api":
            main_api(cfg)

    main()