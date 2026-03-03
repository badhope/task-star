from abc import ABC, abstractmethod
from selenium.webdriver.remote.webelement import WebElement

class BaseStrategy(ABC):
    """答题策略基类"""
    
    @abstractmethod
    def execute(self, element: WebElement, **kwargs):
        """
        执行答题策略
        
        参数:
            element: Selenium WebElement 对象，代表题目容器
            **kwargs: 其他参数，例如填空题的答案池
        """
        pass
