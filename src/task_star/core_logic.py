import time
import random
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .config import config
from .browser import BrowserManager
from .strategies.single import SingleChoiceStrategy
from .strategies.multiple import MultipleChoiceStrategy
from .strategies.blank import FillBlankStrategy
from .exceptions import *
from .utils import logger # 假设你配置了日志模块

class QuestionnaireFiller:
    def __init__(self, status_callback=None, log_callback=None, stop_event=None):
        """
        初始化问卷填写器

        参数说明:
            status_callback: 用于更新UI状态的回调函数 (可选)
            log_callback: 用于在UI显示日志的回调函数 (可选)
            stop_event: threading.Event对象，用于接收停止信号 (可选)
        """
        if config is None:
            raise ConfigError("配置加载失败，请检查 config/config.yaml 文件是否存在且格式正确")

        self.config = config
        self.status_callback = status_callback
        self.log_callback = log_callback
        self.stop_event = stop_event  # 从外部传入的停止事件
        self.driver = None
        # 如果外部没有传入 stop_event，则创建一个内部的事件对象
        if self.stop_event is None:
            self._internal_stop_event = threading.Event()
            self.stop_event = self._internal_stop_event
        
        # 加载选择器配置
        self.selectors = self._load_selectors()
        
        # 初始化策略
        self.strategies = {
            'single': SingleChoiceStrategy(),
            'multiple': MultipleChoiceStrategy(
                min_select=self.config.strategy.get('multi_choice', {}).get('min_select', 2),
                max_select=self.config.strategy.get('multi_choice', {}).get('max_select', 3)
            ),
            'blank': FillBlankStrategy(self.config.strategy.get('fill_blanks', {}))
        }

    def _load_selectors(self):
        """加载选择器配置"""
        # 这里简化处理，实际应从selectors.yaml读取
        # 可以在config.py中统一加载
        from pathlib import Path
        import yaml
        sel_path = Path(__file__).parent.parent.parent / "config" / "selectors.yaml"
        if not sel_path.exists():
            raise ConfigError("selectors.yaml 文件缺失")
        with open(sel_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _update_status(self, msg):
        if self.status_callback:
            self.status_callback(msg)
        logger.info(msg)

    def _log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        logger.info(msg)

    def run(self):
        """
        主运行逻辑，在独立线程中运行
        核心功能: 初始化浏览器，循环填写并提交问卷
        """
        try:
            self._update_status("正在初始化浏览器...")
            # 根据配置创建浏览器管理器，headless参数控制是否显示浏览器窗口
            browser_manager = BrowserManager(headless=self.config.general.get('headless', False))
            self.driver = browser_manager.create_driver()

            # 从配置文件中读取问卷链接和填写次数
            url = self.config.general['questionnaire_url']
            fill_times = self.config.general['fill_times']

            self._log(f"任务开始: 目标 {fill_times} 份")

            success_count = 0
            for i in range(fill_times):
                # 检查是否接收到停止信号
                if self.stop_event.is_set():
                    self._log("用户中止任务")
                    break

                self._update_status(f"正在处理第 {i+1}/{fill_times} 份...")
                try:
                    self._process_one_questionnaire(i+1)
                    success_count += 1
                    self._log(f"第 {i+1} 份完成")
                except CaptchaEncounteredError:
                    # 遇到验证码时的处理逻辑
                    self._log("⚠️ 检测到验证码！请手动完成验证，程序将暂停。")
                    # 这里可以实现一个等待逻辑，比如弹窗提示用户点击继续
                    # 暂时简单处理：暂停并等待用户在UI点击"继续"
                    # 实际项目中可以结合 threading.Event.wait()
                    self._update_status("等待验证码处理...")
                    time.sleep(15)  # 给用户15秒时间处理
                    self._log("继续执行...")
                except Exception as e:
                    # 捕获其他异常，记录日志但继续执行后续任务
                    self._log(f"❌ 第 {i+1} 份失败: {str(e)}")
                    # 失败重试逻辑可以加在这里

                # 随机间隔，模拟真人行为，避免被识别为机器
                interval = self.config.general.get('interval_seconds', 3)
                jitter = random.uniform(0, 2)  # 增加随机抖动，让提交时间更自然
                time.sleep(interval + jitter)

            self._update_status(f"任务结束: 成功 {success_count}/{fill_times}")

        except Exception as e:
            self._log(f"严重错误: {str(e)}")
            self._update_status("发生错误，任务停止")
        finally:
            # 无论成功或失败，都要关闭浏览器
            if self.driver:
                self.driver.quit()

    def _process_one_questionnaire(self, index):
        """
        处理单份问卷的完整流程

        参数说明:
            index: 当前是第几份问卷（用于日志显示）
        """
        # 打开问卷页面
        self.driver.get(self.config.general['questionnaire_url'])

        # 等待页面加载完成，最多等待15秒
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['question_page']['question_container']))
            )
        except TimeoutException:
            raise PageLoadError("页面加载超时，请检查网络或链接")

        # 检测是否出现验证码
        if self._check_captcha():
            raise CaptchaEncounteredError()

        # 获取页面中所有的题目元素
        questions = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['question_page']['question_container'])

        # 遍历每一道题目
        for q_idx, q_element in enumerate(questions):
            # 检查是否接收到停止信号
            if self.stop_event.is_set():
                return

            # 滚动到当前题目，确保可见，模拟人类浏览行为
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", q_element)
            time.sleep(0.5)  # 稍微等待滚动动画完成

            # 识别题目类型并获取题号
            q_type = self._identify_question_type(q_element)
            q_num = q_idx + 1  # 题号从1开始

            try:
                # 根据题目类型调用相应的策略进行答题
                if q_type == 'single':
                    # 单选题策略
                    self.strategies['single'].execute(q_element, selectors=self.selectors)
                elif q_type == 'multiple':
                    # 多选题策略
                    self.strategies['multiple'].execute(q_element, selectors=self.selectors)
                elif q_type == 'blank':
                    # 填空题策略，需要传入题号来获取对应的答案池
                    self.strategies['blank'].execute(q_element, question_number=q_num, selectors=self.selectors)
                else:
                    self._log(f"题目 {q_num}: 未知题型，跳过")
            except Exception as e:
                # 单题出错不影响整体，记录日志继续执行
                self._log(f"题目 {q_num} 处理出错: {e}")

        # 如果配置了自动提交，则点击提交按钮
        if self.config.general.get('auto_submit', True):
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, self.selectors['question_page']['submit_button'])
            submit_btn.click()
            self._log("已点击提交")

    def _check_captcha(self):
        """
        检测是否出现验证码

        返回值:
            True: 检测到验证码
            False: 未检测到验证码
        """
        # 从配置文件中读取验证码检测选择器
        captcha_sel = self.selectors['question_page'].get('captcha_detection')
        if not captcha_sel:
            return False
        try:
            # 尝试查找验证码元素
            el = self.driver.find_element(By.CSS_SELECTOR, captcha_sel)
            return el.is_displayed()
        except NoSuchElementException:
            # 未找到验证码元素，说明没有验证码
            return False

    def _identify_question_type(self, element):
        """
        识别题目类型

        参数说明:
            element: 题目的WebElement对象

        返回值:
            'single': 单选题
            'multiple': 多选题
            'blank': 填空题
            'unknown': 未知题型
        """
        # 使用配置文件中的选择器来判断题目类型
        sp = self.selectors['question_page']

        # 检查是否有单选按钮 (input[type='radio'])
        if element.find_elements(By.CSS_SELECTOR, sp['single_choice']['option']):
            return 'single'

        # 检查是否有复选框 (input[type='checkbox'])
        if element.find_elements(By.CSS_SELECTOR, sp['multiple_choice']['option']):
            return 'multiple'

        # 检查是否有文本输入框 (input[type='text'] 或 textarea)
        if element.find_elements(By.CSS_SELECTOR, sp['fill_blank']['input']):
            return 'blank'

        # 未能识别的题型
        return 'unknown'

    def stop(self):
        """
        停止当前任务
        设置停止事件标志，让run()方法退出循环
        """
        self.stop_event.set()
