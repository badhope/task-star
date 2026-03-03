class TaskStarError(Exception):
    """基础异常类"""
    pass

class ConfigError(TaskStarError):
    """配置相关错误"""
    pass

class BrowserInitError(TaskStarError):
    """浏览器初始化失败"""
    pass

class PageLoadError(TaskStarError):
    """页面加载失败"""
    pass

class CaptchaEncounteredError(TaskStarError):
    """遇到验证码，需要人工干预"""
    pass

class ElementNotFound(TaskStarError):
    """页面元素未找到"""
    pass
