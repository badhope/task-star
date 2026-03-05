from typing import Optional


class TaskStarError(Exception):
    """基础异常类"""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message}\n详情: {self.details}"
        return self.message


class ConfigError(TaskStarError):
    """配置相关错误"""
    pass


class ConfigNotFoundError(ConfigError):
    """配置文件未找到"""
    pass


class ConfigValidationError(ConfigError):
    """配置验证失败"""
    pass


class BrowserInitError(TaskStarError):
    """浏览器初始化失败"""
    pass


class BrowserCrashError(TaskStarError):
    """浏览器崩溃"""
    pass


class PageLoadError(TaskStarError):
    """页面加载失败"""
    pass


class PageTimeoutError(PageLoadError):
    """页面加载超时"""
    pass


class CaptchaEncounteredError(TaskStarError):
    """遇到验证码，需要人工干预"""
    
    def __init__(self, message: str = "检测到验证码，需要人工验证", details: Optional[str] = None):
        super().__init__(message, details)


class ElementNotFound(TaskStarError):
    """页面元素未找到"""
    
    def __init__(self, message: str, selector: Optional[str] = None):
        self.selector = selector
        details = f"选择器: {selector}" if selector else None
        super().__init__(message, details)


class SubmitError(TaskStarError):
    """提交失败"""
    pass


class NetworkError(TaskStarError):
    """网络错误"""
    pass


class StrategyError(TaskStarError):
    """策略执行错误"""
    pass


class ValidationError(TaskStarError):
    """数据验证错误"""
    pass
