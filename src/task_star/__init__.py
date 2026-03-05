"""Task-Star 问卷自动填写助手"""

__version__ = "3.0.0"
__author__ = "Task-Star Team"

from .core_logic import QuestionnaireFiller
from .config import config, ConfigLoader
from .browser import BrowserManager
from .utils import logger
from .error_handler import ErrorHandler, UserNotifier, notify_user, get_error_suggestion

__all__ = [
    "QuestionnaireFiller",
    "ConfigLoader", 
    "BrowserManager",
    "logger",
    "config",
    "ErrorHandler",
    "UserNotifier",
    "notify_user",
    "get_error_suggestion"
]
