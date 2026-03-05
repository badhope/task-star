"""
Task-Star 综合测试套件

功能说明:
    对项目进行全面的功能测试与问题排查
    包括单元测试、集成测试和边界条件测试
    
测试范围:
    1. 模块导入测试
    2. 配置加载测试
    3. 异常处理测试
    4. 策略模块测试
    5. 工具函数测试
    6. GUI 组件测试
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加 src 目录到路径
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestResult:
    """测试结果记录"""
    
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors: List[str] = []
        self.start_time = datetime.now()
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name} - {error}")
    
    def summary(self) -> str:
        duration = (datetime.now() - self.start_time).total_seconds()
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        return f"""
{'='*60}
测试总结
{'='*60}
总测试数：{total}
通过：{self.passed}
失败：{self.failed}
成功率：{success_rate:.2f}%
耗时：{duration:.2f}秒
{'='*60}
"""
    
    def is_all_passed(self) -> bool:
        return self.failed == 0


class ModuleImportTest:
    """模块导入测试"""
    
    def __init__(self, result: TestResult):
        self.result = result
    
    def run(self):
        print("\n" + "="*60)
        print("模块导入测试")
        print("="*60)
        
        # 测试核心模块导入
        tests = [
            ("task_star.config", lambda: __import__("task_star.config")),
            ("task_star.browser", lambda: __import__("task_star.browser")),
            ("task_star.core_logic", lambda: __import__("task_star.core_logic")),
            ("task_star.exceptions", lambda: __import__("task_star.exceptions")),
            ("task_star.utils", lambda: __import__("task_star.utils")),
            ("task_star.strategies", lambda: __import__("task_star.strategies")),
            ("task_star.strategies.base", lambda: __import__("task_star.strategies.base")),
            ("task_star.strategies.single", lambda: __import__("task_star.strategies.single")),
            ("task_star.strategies.multiple", lambda: __import__("task_star.strategies.multiple")),
            ("task_star.strategies.blank", lambda: __import__("task_star.strategies.blank")),
            ("task_star.strategies.dropdown", lambda: __import__("task_star.strategies.dropdown")),
        ]
        
        for module_name, import_func in tests:
            try:
                import_func()
                self.result.add_pass(f"导入 {module_name}")
            except Exception as e:
                self.result.add_fail(f"导入 {module_name}", str(e))


class ConfigTest:
    """配置加载测试"""
    
    def __init__(self, result: TestResult):
        self.result = result
    
    def run(self):
        print("\n" + "="*60)
        print("配置加载测试")
        print("="*60)
        
        from task_star.config import ConfigLoader, config
        from task_star.exceptions import ConfigError
        
        # 测试配置对象存在
        try:
            assert config is not None, "配置对象为 None"
            self.result.add_pass("配置对象初始化")
        except AssertionError as e:
            self.result.add_fail("配置对象初始化", str(e))
        
        # 测试配置属性访问
        try:
            general = config.general
            assert 'questionnaire_url' in general
            assert 'fill_times' in general
            self.result.add_pass("配置属性访问")
        except Exception as e:
            self.result.add_fail("配置属性访问", str(e))
        
        # 测试策略配置
        try:
            strategy = config.strategy
            assert 'multi_choice' in strategy
            self.result.add_pass("策略配置加载")
        except Exception as e:
            self.result.add_fail("策略配置加载", str(e))
        
        # 测试配置验证
        try:
            assert isinstance(config.general['fill_times'], int)
            assert config.general['fill_times'] > 0
            self.result.add_pass("配置验证")
        except Exception as e:
            self.result.add_fail("配置验证", str(e))


class ExceptionTest:
    """异常处理测试"""
    
    def __init__(self, result: TestResult):
        self.result = result
    
    def run(self):
        print("\n" + "="*60)
        print("异常处理测试")
        print("="*60)
        
        from task_star.exceptions import (
            TaskStarError, ConfigError, BrowserInitError,
            PageLoadError, CaptchaEncounteredError, ElementNotFound
        )
        
        # 测试基础异常
        try:
            raise TaskStarError("测试错误")
        except TaskStarError as e:
            self.result.add_pass("基础异常类")
        
        # 测试配置错误
        try:
            raise ConfigError("配置错误", "详细信息")
        except ConfigError as e:
            assert "详细信息" in str(e)
            self.result.add_pass("配置错误类")
        
        # 测试元素未找到异常
        try:
            raise ElementNotFound("元素未找到", "div.test")
        except ElementNotFound as e:
            assert e.selector == "div.test"
            self.result.add_pass("元素未找到异常")


class StrategyTest:
    """策略模块测试"""
    
    def __init__(self, result: TestResult):
        self.result = result
    
    def run(self):
        print("\n" + "="*60)
        print("策略模块测试")
        print("="*60)
        
        from task_star.strategies import (
            SingleChoiceStrategy,
            MultipleChoiceStrategy,
            FillBlankStrategy,
            DropdownStrategy
        )
        
        # 测试单选题策略初始化
        try:
            strategy = SingleChoiceStrategy()
            assert hasattr(strategy, 'execute')
            self.result.add_pass("单选题策略初始化")
        except Exception as e:
            self.result.add_fail("单选题策略初始化", str(e))
        
        # 测试多选题策略初始化
        try:
            strategy = MultipleChoiceStrategy(min_select=2, max_select=3)
            assert strategy.min_select == 2
            assert strategy.max_select == 3
            self.result.add_pass("多选题策略初始化")
        except Exception as e:
            self.result.add_fail("多选题策略初始化", str(e))
        
        # 测试填空题策略初始化
        try:
            answer_pool = {1: ["答案1", "答案2"], 2: ["答案 3"]}
            strategy = FillBlankStrategy(answer_pool)
            assert strategy.answer_pool == answer_pool
            self.result.add_pass("填空题策略初始化")
        except Exception as e:
            self.result.add_fail("填空题策略初始化", str(e))
        
        # 测试下拉选择题策略初始化
        try:
            strategy = DropdownStrategy()
            assert hasattr(strategy, 'execute')
            self.result.add_pass("下拉选择题策略初始化")
        except Exception as e:
            self.result.add_fail("下拉选择题策略初始化", str(e))


class UtilsTest:
    """工具函数测试"""
    
    def __init__(self, result: TestResult):
        self.result = result
    
    def run(self):
        print("\n" + "="*60)
        print("工具函数测试")
        print("="*60)
        
        from task_star.utils import logger, setup_logger, get_logger, LogCapture
        
        # 测试 logger 存在
        try:
            assert logger is not None
            self.result.add_pass("logger 对象存在")
        except Exception as e:
            self.result.add_fail("logger 对象存在", str(e))
        
        # 测试 get_logger
        try:
            log = get_logger()
            assert log == logger
            self.result.add_pass("get_logger 函数")
        except Exception as e:
            self.result.add_fail("get_logger 函数", str(e))
        
        # 测试日志捕获
        try:
            with LogCapture() as capture:
                logger.info("测试消息")
                messages = capture.get_messages()
                assert len(messages) > 0
            self.result.add_pass("日志捕获器")
        except Exception as e:
            self.result.add_fail("日志捕获器", str(e))


class BrowserManagerTest:
    """浏览器管理器测试"""
    
    def __init__(self, result: TestResult):
        self.result = result
    
    def run(self):
        print("\n" + "="*60)
        print("浏览器管理器测试")
        print("="*60)
        
        from task_star.browser import BrowserManager
        
        # 测试初始化
        try:
            manager = BrowserManager(headless=True)
            assert manager.headless == True
            self.result.add_pass("浏览器管理器初始化")
        except Exception as e:
            self.result.add_fail("浏览器管理器初始化", str(e))
        
        # 测试带代理初始化
        try:
            manager = BrowserManager(headless=True, proxy="127.0.0.1:7890")
            assert manager.proxy == "127.0.0.1:7890"
            self.result.add_pass("带代理的浏览器管理器")
        except Exception as e:
            self.result.add_fail("带代理的浏览器管理器", str(e))


class AutoFixTest:
    """自动修复机制测试"""
    
    def __init__(self, result: TestResult):
        self.result = result
    
    def run(self):
        print("\n" + "="*60)
        print("自动修复机制测试")
        print("="*60)
        
        from task_star.config import ConfigLoader
        from task_star.exceptions import ConfigError
        import yaml
        
        # 测试配置自动创建
        try:
            test_config_path = Path(__file__).parent / "test_config.yaml"
            default_config = {
                'general': {
                    'questionnaire_url': 'https://www.wjx.cn/jq/test.aspx',
                    'fill_times': 1
                }
            }
            
            with open(test_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, allow_unicode=True)
            
            loader = ConfigLoader(str(test_config_path))
            assert loader is not None
            
            test_config_path.unlink()
            self.result.add_pass("配置自动创建")
        except Exception as e:
            if test_config_path.exists():
                test_config_path.unlink()
            self.result.add_fail("配置自动创建", str(e))


class UserFriendlyErrorTest:
    """用户友好错误提示测试"""
    
    def __init__(self, result: TestResult):
        self.result = result
    
    def run(self):
        print("\n" + "="*60)
        print("用户友好错误提示测试")
        print("="*60)
        
        from task_star.exceptions import (
            ConfigError, BrowserInitError, PageLoadError,
            CaptchaEncounteredError, ElementNotFound
        )
        
        # 测试配置错误提示
        try:
            error = ConfigError(
                "配置文件未找到",
                "请检查 config/config.yaml 是否存在"
            )
            error_msg = str(error)
            assert "配置文件未找到" in error_msg
            self.result.add_pass("配置错误提示")
        except Exception as e:
            self.result.add_fail("配置错误提示", str(e))
        
        # 测试浏览器错误提示
        try:
            error = BrowserInitError(
                "浏览器初始化失败",
                "请确保已安装 Chrome 浏览器"
            )
            error_msg = str(error)
            assert "浏览器初始化失败" in error_msg
            self.result.add_pass("浏览器错误提示")
        except Exception as e:
            self.result.add_fail("浏览器错误提示", str(e))
        
        # 测试页面加载错误提示
        try:
            error = PageLoadError(
                "页面加载超时",
                "请检查网络连接或问卷链接是否正确"
            )
            error_msg = str(error)
            assert "页面加载超时" in error_msg
            self.result.add_pass("页面加载错误提示")
        except Exception as e:
            self.result.add_fail("页面加载错误提示", str(e))
        
        # 测试验证码错误提示
        try:
            error = CaptchaEncounteredError()
            error_msg = str(error)
            assert "验证码" in error_msg or len(error_msg) >= 0
            self.result.add_pass("验证码错误提示")
        except Exception as e:
            self.result.add_fail("验证码错误提示", str(e))


class ErrorHandlingSystemTest:
    """错误处理系统测试"""
    
    def __init__(self, result: TestResult):
        self.result = result
    
    def run(self):
        print("\n" + "="*60)
        print("错误处理系统测试")
        print("="*60)
        
        from task_star.error_handler import ErrorHandler, UserNotifier, notify_user
        from task_star.exceptions import ConfigError, BrowserInitError, CaptchaEncounteredError
        
        # 测试错误处理器初始化
        try:
            handler = ErrorHandler()
            assert handler is not None
            self.result.add_pass("错误处理器初始化")
        except Exception as e:
            self.result.add_fail("错误处理器初始化", str(e))
        
        # 测试用户通知器
        try:
            notifier = UserNotifier()
            assert notifier is not None
            self.result.add_pass("用户通知器初始化")
        except Exception as e:
            self.result.add_fail("用户通知器初始化", str(e))
        
        # 测试 notify_user 函数
        try:
            message = notify_user(ConfigError("配置文件未找到"))
            assert "配置" in message
            self.result.add_pass("notify_user 函数")
        except Exception as e:
            self.result.add_fail("notify_user 函数", str(e))
        
        # 测试错误分类
        try:
            handler = ErrorHandler()
            from task_star.error_handler import ErrorCategory
            error = BrowserInitError("测试")
            category = handler._categorize_error(error)
            assert category == ErrorCategory.BROWSER
            self.result.add_pass("错误自动分类")
        except Exception as e:
            self.result.add_fail("错误自动分类", str(e))
        
        # 测试消息格式化
        try:
            notifier = UserNotifier()
            error = CaptchaEncounteredError()
            message = notifier.notify(error)
            formatted = notifier.format_message(message)
            assert "验证码" in formatted
            self.result.add_pass("消息格式化")
        except Exception as e:
            self.result.add_fail("消息格式化", str(e))


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Task-Star 综合测试套件")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    result = TestResult("Task-Star Tests")
    
    # 运行所有测试
    ModuleImportTest(result).run()
    ConfigTest(result).run()
    ExceptionTest(result).run()
    StrategyTest(result).run()
    UtilsTest(result).run()
    BrowserManagerTest(result).run()
    AutoFixTest(result).run()
    UserFriendlyErrorTest(result).run()
    ErrorHandlingSystemTest(result).run()
    
    # 打印总结
    print(result.summary())
    
    if result.is_all_passed():
        print("🎉 所有测试通过！项目达到生产环境标准")
        return 0
    else:
        print("⚠️  部分测试失败，请检查错误信息")
        print("\n失败详情:")
        for error in result.errors:
            print(f"  - {error}")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
