"""自定义异常类"""


class TaskStarError(Exception):
    """基础异常类"""
    pass


class ConfigError(TaskStarError):
    """配置错误"""
    pass


class BrowserInitError(TaskStarError):
    """浏览器初始化错误"""
    pass


class PageLoadError(TaskStarError):
    """页面加载错误"""
    pass


class CaptchaRequired(TaskStarError):
    """需要验证码"""
    pass
