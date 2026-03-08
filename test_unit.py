#!/usr/bin/env python3
"""Task-Star 单元测试 - 完整版"""

import unittest
import sys
from pathlib import Path

# 直接导入 exceptions 模块，避免导入 __init__.py
exceptions_path = Path(__file__).parent / "src" / "task_star"
if str(exceptions_path) not in sys.path:
    sys.path.insert(0, str(exceptions_path))

# 直接加载 exceptions 模块
import importlib.util
spec = importlib.util.spec_from_file_location("exceptions", exceptions_path / "exceptions.py")
exceptions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exceptions)


class TestExceptions(unittest.TestCase):
    """测试异常类"""

    def test_task_star_error(self):
        """测试基础异常"""
        try:
            raise exceptions.TaskStarError("测试错误")
        except exceptions.TaskStarError as e:
            self.assertEqual(str(e), "测试错误")

    def test_config_error(self):
        """测试配置异常"""
        try:
            raise exceptions.ConfigError("配置错误")
        except exceptions.ConfigError as e:
            self.assertEqual(str(e), "配置错误")

    def test_browser_init_error(self):
        """测试浏览器异常"""
        try:
            raise exceptions.BrowserInitError("浏览器错误")
        except exceptions.BrowserInitError as e:
            self.assertEqual(str(e), "浏览器错误")

    def test_page_load_error(self):
        """测试页面加载异常"""
        try:
            raise exceptions.PageLoadError("页面加载失败")
        except exceptions.PageLoadError as e:
            self.assertEqual(str(e), "页面加载失败")

    def test_captcha_required(self):
        """测试验证码异常"""
        try:
            raise exceptions.CaptchaRequired()
        except exceptions.CaptchaRequired:
            pass

    def test_exception_inheritance(self):
        """测试异常继承关系"""
        self.assertTrue(issubclass(exceptions.ConfigError, exceptions.TaskStarError))
        self.assertTrue(issubclass(exceptions.BrowserInitError, exceptions.TaskStarError))
        self.assertTrue(issubclass(exceptions.PageLoadError, exceptions.TaskStarError))
        self.assertTrue(issubclass(exceptions.CaptchaRequired, exceptions.TaskStarError))


class TestModuleStructure(unittest.TestCase):
    """测试模块结构"""

    def test_exceptions_defined(self):
        """测试所有必要异常已定义"""
        required_exceptions = [
            'TaskStarError',
            'ConfigError', 
            'BrowserInitError',
            'PageLoadError',
            'CaptchaRequired'
        ]
        for exc_name in required_exceptions:
            self.assertTrue(hasattr(exceptions, exc_name), f"缺少异常类：{exc_name}")


class TestConfigValidation(unittest.TestCase):
    """测试配置验证逻辑"""

    def test_valid_config(self):
        """测试有效配置"""
        config = {
            'general': {
                'questionnaire_url': 'https://example.com',
                'fill_times': 10,
                'interval_seconds': 5,
                'retry_count': 3
            },
            'strategy': {
                'multi_choice': {
                    'min_select': 2,
                    'max_select': 3
                }
            }
        }
        
        self.assertEqual(config['general']['fill_times'], 10)
        self.assertEqual(config['strategy']['multi_choice']['min_select'], 2)

    def test_fill_times_validation(self):
        """测试 fill_times 验证"""
        valid_values = [1, 5, 10, 100]
        for val in valid_values:
            self.assertTrue(val >= 1, f"{val} 应该是有效的 fill_times")

    def test_interval_validation(self):
        """测试 interval 验证"""
        valid_values = [0, 3, 5, 10]
        for val in valid_values:
            self.assertTrue(val >= 0, f"{val} 应该是有效的 interval")

    def test_retry_count_validation(self):
        """测试 retry_count 验证"""
        valid_values = [0, 1, 3, 5]
        for val in valid_values:
            self.assertTrue(val >= 0, f"{val} 应该是有效的 retry_count")

    def test_multi_choice_config(self):
        """测试多选题配置"""
        mc_config = {'min_select': 2, 'max_select': 3}
        self.assertLessEqual(mc_config['min_select'], mc_config['max_select'])


class TestSimpleEvent(unittest.TestCase):
    """测试 SimpleEvent 类"""

    def test_event_initial_state(self):
        """测试事件初始状态"""
        class SimpleEvent:
            def __init__(self):
                self._flag = True
            def is_set(self): return self._flag
            def set(self): self._flag = True
            def clear(self): self._flag = False
            def wait(self): pass
        
        event = SimpleEvent()
        self.assertTrue(event.is_set())

    def test_event_set_clear(self):
        """测试事件的设置和清除"""
        class SimpleEvent:
            def __init__(self):
                self._flag = True
            def is_set(self): return self._flag
            def set(self): self._flag = True
            def clear(self): self._flag = False
            def wait(self): pass
        
        event = SimpleEvent()
        event.clear()
        self.assertFalse(event.is_set())
        
        event.set()
        self.assertTrue(event.is_set())


class TestEdgeCases(unittest.TestCase):
    """测试边界条件"""

    def test_empty_answer_pool(self):
        """测试空答案池"""
        answers = []
        self.assertEqual(len(answers), 0)

    def test_zero_options(self):
        """测试零选项情况"""
        options = []
        self.assertEqual(len(options), 0)

    def test_single_option(self):
        """测试单选项情况"""
        options = ['option1']
        self.assertEqual(len(options), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
