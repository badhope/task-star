"""Task-Star 问卷自动填写助手"""

__version__ = "1.0.0"
__author__ = "Task-Star Team"

from .core_logic import QuestionnaireFiller
from .config import config, ConfigLoader
from .browser import BrowserManager
from .utils import logger

__all__ = [
    "QuestionnaireFiller",
    "ConfigLoader", 
    "BrowserManager",
    "logger",
    "config"
]
