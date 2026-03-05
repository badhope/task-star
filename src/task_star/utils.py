import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


_log_file_initialized = False


def _ensure_log_dir():
    """确保日志目录存在"""
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logger(level=logging.INFO, log_file: Optional[str] = None):
    """
    设置日志级别和输出文件

    参数说明:
        level: 日志级别，默认为 logging.INFO
        log_file: 日志文件路径，如果指定则将日志同时输出到文件

    返回值:
        配置好的logger对象
    """
    global _log_file_initialized
    
    logger.setLevel(level)
    
    if log_file is None and not _log_file_initialized:
        log_dir = _ensure_log_dir()
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"taskstar_{timestamp}.log"
        _log_file_initialized = True
    
    if log_file and not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('TaskStar')

setup_logger()


def get_logger():
    """
    获取全局logger对象

    返回值:
        全局logger实例
    """
    return logger


class LogCapture:
    """日志捕获器，用于捕获日志消息"""
    
    def __init__(self):
        self.messages = []
        self._handler = None
    
    def __enter__(self):
        self._handler = logging.Handler()
        self._handler.emit = lambda record: self.messages.append(
            self._handler.format(record)
        )
        self._handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(self._handler)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._handler:
            logger.removeHandler(self._handler)
        return False
    
    def get_messages(self) -> list:
        return self.messages
    
    def clear(self):
        self.messages.clear()
