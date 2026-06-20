"""
Sistema centralizado de logging para o BeaverSec.
Suporta níveis (INFO, DEBUG, ERROR) e formatação padronizada.
"""
import logging
import sys
from typing import Optional

_LOGGER_INSTANCE: Optional[logging.Logger] = None

def setup_logger(
    name: str = "BeaverSec",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    global _LOGGER_INSTANCE
    
    if _LOGGER_INSTANCE is not None:
        return _LOGGER_INSTANCE
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-7s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Não foi possível criar arquivo de log '{log_file}': {e}")
    
    _LOGGER_INSTANCE = logger
    return logger

def get_logger() -> logging.Logger:
    global _LOGGER_INSTANCE
    if _LOGGER_INSTANCE is None:
        return setup_logger()
    return _LOGGER_INSTANCE