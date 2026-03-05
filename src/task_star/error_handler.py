"""
错误处理与用户提示系统

功能说明:
    - 统一的错误处理机制
    - 自动修复常见错误
    - 分级用户提示系统
    - 错误恢复建议
"""

from enum import Enum
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
import logging


class ErrorLevel(Enum):
    """错误级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误分类"""
    CONFIG = "config"
    BROWSER = "browser"
    NETWORK = "network"
    PAGE = "page"
    STRATEGY = "strategy"
    VALIDATION = "validation"
    OTHER = "other"


@dataclass
class UserMessage:
    """用户消息"""
    title: str
    content: str
    level: ErrorLevel
    category: ErrorCategory
    suggestion: Optional[str] = None
    auto_fix_available: bool = False
    auto_fix_action: Optional[Callable] = None


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger('TaskStar.ErrorHandler')
        self.error_handlers: Dict[ErrorCategory, List[Callable]] = {
            ErrorCategory.CONFIG: [],
            ErrorCategory.BROWSER: [],
            ErrorCategory.NETWORK: [],
            ErrorCategory.PAGE: [],
            ErrorCategory.STRATEGY: [],
            ErrorCategory.VALIDATION: [],
            ErrorCategory.OTHER: [],
        }
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """设置默认错误处理器"""
        
        # 配置错误自动修复
        @self.register_handler(ErrorCategory.CONFIG)
        def auto_fix_config(error: Exception) -> Optional[UserMessage]:
            from task_star.config import ConfigLoader
            from task_star.exceptions import ConfigError
            
            error_msg = str(error).lower()
            
            if '未找到' in error_msg or 'not found' in error_msg:
                return UserMessage(
                    title="配置文件未找到",
                    content="系统未找到配置文件，正在尝试自动创建默认配置",
                    level=ErrorLevel.WARNING,
                    category=ErrorCategory.CONFIG,
                    suggestion="默认配置文件已创建，请检查 config/config.yaml",
                    auto_fix_available=True,
                    auto_fix_action=lambda: ConfigLoader.create_default("config/config.yaml")
                )
            
            if '格式错误' in error_msg or 'format' in error_msg:
                return UserMessage(
                    title="配置文件格式错误",
                    content="配置文件的 YAML 格式不正确",
                    level=ErrorLevel.ERROR,
                    category=ErrorCategory.CONFIG,
                    suggestion="请检查配置文件语法，确保是正确的 YAML 格式"
                )
            
            return None
        
        # 浏览器错误自动修复
        @self.register_handler(ErrorCategory.BROWSER)
        def auto_fix_browser(error: Exception) -> Optional[UserMessage]:
            from task_star.exceptions import BrowserInitError
            
            error_msg = str(error).lower()
            
            if 'chrome' in error_msg and ('未找到' in error_msg or 'not found' in error_msg):
                return UserMessage(
                    title="Chrome 浏览器未找到",
                    content="系统未安装 Google Chrome 浏览器",
                    level=ErrorLevel.CRITICAL,
                    category=ErrorCategory.BROWSER,
                    suggestion="请安装 Chrome 浏览器：https://www.google.com/chrome/"
                )
            
            if 'chromedriver' in error_msg or 'driver' in error_msg:
                return UserMessage(
                    title="ChromeDriver 问题",
                    content="ChromeDriver 版本不匹配或未找到",
                    level=ErrorLevel.ERROR,
                    category=ErrorCategory.BROWSER,
                    suggestion="运行命令：pip install --upgrade webdriver-manager",
                    auto_fix_available=True
                )
            
            return None
        
        # 网络错误处理
        @self.register_handler(ErrorCategory.NETWORK)
        def auto_fix_network(error: Exception) -> Optional[UserMessage]:
            error_msg = str(error).lower()
            
            if 'timeout' in error_msg or '超时' in error_msg:
                return UserMessage(
                    title="网络连接超时",
                    content="无法连接到问卷服务器",
                    level=ErrorLevel.ERROR,
                    category=ErrorCategory.NETWORK,
                    suggestion="请检查网络连接，或稍后重试"
                )
            
            if 'connection' in error_msg or '连接' in error_msg:
                return UserMessage(
                    title="网络连接失败",
                    content="无法建立网络连接",
                    level=ErrorLevel.ERROR,
                    category=ErrorCategory.NETWORK,
                    suggestion="检查网络设置和防火墙配置"
                )
            
            return None
        
        # 页面错误处理
        @self.register_handler(ErrorCategory.PAGE)
        def auto_fix_page(error: Exception) -> Optional[UserMessage]:
            error_msg = str(error).lower()
            
            if 'element' in error_msg or '元素' in error_msg:
                return UserMessage(
                    title="页面元素未找到",
                    content="无法在页面中找到所需的元素",
                    level=ErrorLevel.WARNING,
                    category=ErrorCategory.PAGE,
                    suggestion="问卷页面结构可能已更新，请更新 selectors.yaml 配置文件"
                )
            
            if 'captcha' in error_msg or '验证码' in error_msg:
                return UserMessage(
                    title="检测到验证码",
                    content="问卷需要人工验证",
                    level=ErrorLevel.INFO,
                    category=ErrorCategory.PAGE,
                    suggestion="请在浏览器窗口中手动完成验证码，然后点击'继续'按钮"
                )
            
            return None
    
    def register_handler(self, category: ErrorCategory):
        """注册错误处理器"""
        def decorator(func: Callable[[Exception], Optional[UserMessage]]):
            self.error_handlers[category].append(func)
            return func
        return decorator
    
    def handle_error(self, error: Exception, category: Optional[ErrorCategory] = None) -> UserMessage:
        """
        处理错误并返回用户消息
        
        参数:
            error: 异常对象
            category: 错误分类，如果为 None 则自动判断
        
        返回:
            UserMessage 对象
        """
        # 自动判断错误分类
        if category is None:
            category = self._categorize_error(error)
        
        # 尝试使用注册的处理器
        for handler in self.error_handlers.get(category, []):
            try:
                message = handler(error)
                if message:
                    self.logger.info(f"错误已处理：{message.title}")
                    return message
            except Exception as e:
                self.logger.error(f"错误处理器执行失败：{e}")
        
        # 返回默认消息
        return self._create_default_message(error, category)
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """自动判断错误分类"""
        from task_star.exceptions import (
            ConfigError, BrowserInitError, PageLoadError,
            CaptchaEncounteredError, ElementNotFound, NetworkError
        )
        
        error_name = type(error).__name__.lower()
        error_msg = str(error).lower()
        
        if isinstance(error, ConfigError) or 'config' in error_name:
            return ErrorCategory.CONFIG
        
        if isinstance(error, BrowserInitError) or 'browser' in error_name:
            return ErrorCategory.BROWSER
        
        if isinstance(error, (PageLoadError, ElementNotFound, CaptchaEncounteredError)):
            return ErrorCategory.PAGE
        
        if isinstance(error, NetworkError) or any(kw in error_msg for kw in ['network', 'timeout', 'connection']):
            return ErrorCategory.NETWORK
        
        if 'strategy' in error_name:
            return ErrorCategory.STRATEGY
        
        if 'validation' in error_name or 'valid' in error_msg:
            return ErrorCategory.VALIDATION
        
        return ErrorCategory.OTHER
    
    def _create_default_message(self, error: Exception, category: ErrorCategory) -> UserMessage:
        """创建默认错误消息"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        level_map = {
            ErrorCategory.CONFIG: ErrorLevel.ERROR,
            ErrorCategory.BROWSER: ErrorLevel.ERROR,
            ErrorCategory.NETWORK: ErrorLevel.ERROR,
            ErrorCategory.PAGE: ErrorLevel.WARNING,
            ErrorCategory.STRATEGY: ErrorLevel.WARNING,
            ErrorCategory.VALIDATION: ErrorLevel.WARNING,
            ErrorCategory.OTHER: ErrorLevel.ERROR,
        }
        
        suggestion_map = {
            ErrorCategory.CONFIG: "请检查配置文件是否正确",
            ErrorCategory.BROWSER: "请确保已安装 Chrome 浏览器并更新 ChromeDriver",
            ErrorCategory.NETWORK: "请检查网络连接后重试",
            ErrorCategory.PAGE: "请检查页面元素或更新选择器配置",
            ErrorCategory.STRATEGY: "请检查答题策略配置",
            ErrorCategory.VALIDATION: "请检查输入数据格式",
            ErrorCategory.OTHER: "如果问题持续，请查看日志文件获取详细信息",
        }
        
        return UserMessage(
            title=f"{error_type} 发生",
            content=error_msg,
            level=level_map.get(category, ErrorLevel.ERROR),
            category=category,
            suggestion=suggestion_map.get(category)
        )


class UserNotifier:
    """用户通知器"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.message_queue: List[UserMessage] = []
        self.logger = logging.getLogger('TaskStar.Notifier')
    
    def notify(self, error: Exception, category: Optional[ErrorCategory] = None) -> UserMessage:
        """
        通知用户错误信息
        
        参数:
            error: 异常对象
            category: 错误分类
        
        返回:
            UserMessage 对象
        """
        message = self.error_handler.handle_error(error, category)
        self.message_queue.append(message)
        
        # 根据级别记录日志
        log_method = {
            ErrorLevel.INFO: self.logger.info,
            ErrorLevel.WARNING: self.logger.warning,
            ErrorLevel.ERROR: self.logger.error,
            ErrorLevel.CRITICAL: self.logger.critical,
        }.get(message.level, self.logger.error)
        
        log_method(f"[{message.category.value}] {message.title}: {message.content}")
        
        return message
    
    def get_messages(self, level: Optional[ErrorLevel] = None) -> List[UserMessage]:
        """获取消息队列"""
        if level:
            return [m for m in self.message_queue if m.level == level]
        return self.message_queue
    
    def clear(self):
        """清空消息队列"""
        self.message_queue.clear()
    
    def format_message(self, message: UserMessage) -> str:
        """格式化消息为字符串"""
        level_icons = {
            ErrorLevel.INFO: "ℹ️",
            ErrorLevel.WARNING: "⚠️",
            ErrorLevel.ERROR: "❌",
            ErrorLevel.CRITICAL: "🔴",
        }
        
        formatted = f"{level_icons.get(message.level, '❓')} {message.title}\n"
        formatted += f"   {message.content}\n"
        
        if message.suggestion:
            formatted += f"   💡 建议：{message.suggestion}\n"
        
        if message.auto_fix_available:
            formatted += f"   🔧 支持自动修复\n"
        
        return formatted


# 全局通知器实例
notifier = UserNotifier()


def notify_user(error: Exception, category: Optional[ErrorCategory] = None) -> str:
    """
    便捷函数：通知用户错误
    
    参数:
        error: 异常对象
        category: 错误分类
    
    返回:
        格式化的消息字符串
    """
    message = notifier.notify(error, category)
    return notifier.format_message(message)


def get_error_suggestion(error: Exception) -> str:
    """
    获取错误建议
    
    参数:
        error: 异常对象
    
    返回:
        建议字符串
    """
    message = notifier.notify(error)
    return message.suggestion or "如果问题持续，请查看日志文件"
