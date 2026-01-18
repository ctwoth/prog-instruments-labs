# file: game_logger.py
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Настройка системы логирования"""
    # Создаем директорию для логов, если её нет
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{log_dir}/tetris_{timestamp}.log"

    # формат логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    logger = logging.getLogger('TetrisLite')
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=1048576,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)

    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Система логирования инициализирована. Логи пишутся в: {log_filename}")
    logger.info(f"Игровой процесс начнется с уровня: {logger.getEffectiveLevel()}")

    return logger


logger = setup_logging()
