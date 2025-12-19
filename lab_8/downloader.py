import aiofiles
import aiohttp
import asyncio
import logging
import json
import csv
import os
from pathlib import Path
from urllib.parse import urlparse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Загружаем конфигурацию из JSON файла"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        return config
        
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise ValueError("file didn't exist")
        

class AsyncImageDownloader:
    def __init__(self, config_path: str = "config.json"):
        self.config = load_config(config_path)
        self.session = None
        self.semaphore = asyncio.Semaphore(self.config['MAX_CONCURRENT'])
        self.success_count = 0
        self.error_count = 0

        Path(self.config['TARGET_DIRECTORY']).mkdir(parents=True, exist_ok=True)
    
    async def _get_session(self):
        """Создаём aiohttp сессию"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.config['TIMEOUT'])
            connector = aiohttp.TCPConnector(limit=self.config['MAX_CONCURRENT'])
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
            self.semaphore = asyncio.Semaphore(self.config['MAX_CONCURRENT'])
        return self.session

    async def download_all(self):
        """Качаем все изображения"""
        # ещё нет)

