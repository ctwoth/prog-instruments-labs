import aiofiles
import aiohttp
import asyncio
import logging
import json
import csv
import os
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
from typing import List, Tuple
from tqdm.asyncio import tqdm_asyncio

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

    async def _download_single(self, url: str, pbar: tqdm_asyncio) -> Tuple[bool, str]:
        """Скачать одно изображение"""
        async with self.semaphore:
            for attempt in range(self.config['RETRY_COUNT']):
                try:
                    session = await self._get_session()

                    async with session.get(url, allow_redirects=True) as response:
                        if response.status != 200:
                            error_msg = f"HTTP {response.status}"
                            raise Exception(error_msg)

                        # Проверить content-type
                        content_type = response.headers.get('Content-Type', '')
                        if not content_type.startswith('image/'):
                            raise Exception(f"Not an image: {content_type}")

                        # Определить имя файла
                        filename = _get_filename_from_url(url)
                        filepath = Path(self.config['TARGET_DIRECTORY']) / filename

                        # Сохранить файл
                        async with aiofiles.open(filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)

                        logger.debug(f"Downloaded: {filename} ({response.headers.get('Content-Length', '?')} bytes)")
                        return True, filename

                except asyncio.TimeoutError:
                    logger.warning(f"Timeout (attempt {attempt + 1}/{self.config['RETRY_COUNT']}): {url}")
                    if attempt == self.config['RETRY_COUNT'] - 1:
                        return False, "Timeout"

                except Exception as e:
                    logger.warning(f"Error (attempt {attempt + 1}/{self.config['RETRY_COUNT']}): {url} - {str(e)}")
                    if attempt == self.config['RETRY_COUNT'] - 1:
                        return False, str(e)

                # Пауза перед повторной попыткой
                if attempt < self.config['RETRY_COUNT'] - 1:
                    await asyncio.sleep(1 * (attempt + 1))

            return False, "Max retries exceeded"

    def _read_urls_from_csv(self) -> List[str]:
        """Читаем URL из CSV файла"""
        urls = []
        try:
            with open(self.config['CSV_PATH'], 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # Проверяем, что строка не пустая
                        url = row[0].strip()
                        if url and url.startswith(('http://', 'https://')):
                            urls.append(url)

            logger.info(f"Loaded {len(urls)} URLs from {self.config['CSV_PATH']}")
            return urls

        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.config['CSV_PATH']}")
            return []
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return []

    async def download_all(self):
        """Качаем все изображения"""
        urls = self._read_urls_from_csv()
        if not urls:
            logger.error("No URLs to download")
            return

        logger.info(f"Starting download of {len(urls)} images")
        logger.info(f"Target directory: {self.config['TARGET_DIRECTORY']}")
        logger.info(f"Max concurrent: {self.config['MAX_CONCURRENT']}")

        start_time = datetime.now()

        # Создаём задачи для скачивания
        tasks = []
        with tqdm_asyncio(total=len(urls), desc="Downloading", unit="img") as pbar:
            for url in urls:
                task = asyncio.create_task(self._download_single(url, pbar))
                task.add_done_callback(lambda f, pb=pbar: pb.update(1))
                tasks.append(task)

            # Обработываем результат
            for task in asyncio.as_completed(tasks):
                success, message = await task
                if success:
                    self.success_count += 1
                else:
                    self.error_count += 1

        # Конец скачки
        if self.session:
            await self.session.close()

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 50)
        logger.info(f"Download completed in {elapsed:.2f} seconds")
        logger.info(f"Successfully downloaded: {self.success_count}")
        logger.info(f"Failed: {self.error_count}")
        logger.info(f"Directory: {self.config['TARGET_DIRECTORY']}")



