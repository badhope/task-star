import time
import random
import threading
from typing import Optional, Callable, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from .config import config
from .browser import BrowserManager
from .strategies.single import SingleChoiceStrategy
from .strategies.multiple import MultipleChoiceStrategy
from .strategies.blank import FillBlankStrategy
from .strategies.dropdown import DropdownStrategy
from .exceptions import *
from .utils import logger


class QuestionnaireFiller:
    def __init__(self, status_callback: Optional[Callable] = None, 
                 log_callback: Optional[Callable] = None, 
                 progress_callback: Optional[Callable] = None,
                 stop_event: Optional[threading.Event] = None):
        """
        初始化问卷填写器

        参数说明:
            status_callback: 用于更新UI状态的回调函数 (可选)
            log_callback: 用于在UI显示日志的回调函数 (可选)
            progress_callback: 用于更新进度条的回调函数，参数为(current, total) (可选)
            stop_event: threading.Event对象，用于接收停止信号 (可选)
        """
        if config is None:
            raise ConfigError("配置加载失败，请检查 config/config.yaml 文件是否存在且格式正确")

        self.config = config
        self.status_callback = status_callback
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.stop_event = stop_event
        self.driver = None
        self.browser_manager = None
        
        if self.stop_event is None:
            self._internal_stop_event = threading.Event()
            self.stop_event = self._internal_stop_event
        
        self._captcha_wait_event = threading.Event()
        self._captcha_wait_event.set()
        
        self.selectors = self._load_selectors()
        
        self.strategies = {
            'single': SingleChoiceStrategy(),
            'multiple': MultipleChoiceStrategy(
                min_select=self.config.strategy.get('multi_choice', {}).get('min_select', 2),
                max_select=self.config.strategy.get('multi_choice', {}).get('max_select', 3)
            ),
            'blank': FillBlankStrategy(self.config.strategy.get('fill_blanks', {})),
            'dropdown': DropdownStrategy()
        }
        
        self._success_count = 0
        self._fail_count = 0
        self._retry_count = self.config.general.get('retry_count', 3)

    def _load_selectors(self) -> Dict[str, Any]:
        """加载选择器配置"""
        from pathlib import Path
        import yaml
        sel_path = Path(__file__).parent.parent.parent / "config" / "selectors.yaml"
        if not sel_path.exists():
            logger.warning("selectors.yaml 文件缺失，使用默认选择器")
            return self._get_default_selectors()
        try:
            with open(sel_path, 'r', encoding='utf-8') as f:
                selectors = yaml.safe_load(f)
                return selectors if selectors else self._get_default_selectors()
        except Exception as e:
            logger.error(f"加载选择器配置失败: {e}")
            return self._get_default_selectors()
    
    def _get_default_selectors(self) -> Dict[str, Any]:
        """获取默认选择器配置"""
        return {
            'question_page': {
                'question_container': "div.field",
                'submit_button': "input#submit_button, button#submit_button",
                'single_choice': {
                    'option': "input[type='radio']",
                    'alternative': "div.radio-div"
                },
                'multiple_choice': {
                    'option': "input[type='checkbox']",
                    'alternative': "div.checkbox-div"
                },
                'fill_blank': {
                    'input': "input[type='text'], textarea"
                },
                'dropdown': {
                    'select': "select"
                },
                'captcha_detection': "div#divCaptcha, div.geetest_panel",
                'success_indicator': "div.success, div#success_page"
            }
        }

    def _update_status(self, msg: str):
        """更新状态"""
        if self.status_callback:
            try:
                self.status_callback(msg)
            except Exception as e:
                logger.error(f"状态回调执行失败: {e}")
        logger.info(msg)

    def _log(self, msg: str, level: str = "INFO"):
        """记录日志"""
        if self.log_callback:
            try:
                self.log_callback(msg)
            except Exception as e:
                logger.error(f"日志回调执行失败: {e}")
        
        log_level = getattr(logger, level.lower(), logger.info)
        log_level(msg)

    def _update_progress(self, current: int, total: int):
        """更新进度"""
        if self.progress_callback:
            try:
                self.progress_callback(current, total)
            except Exception as e:
                logger.error(f"进度回调执行失败: {e}")

    def run(self):
        """
        主运行逻辑，在独立线程中运行
        核心功能: 初始化浏览器，循环填写并提交问卷
        """
        try:
            self._update_status("正在初始化浏览器...")
            
            headless = self.config.general.get('headless', False)
            proxy = self.config.general.get('proxy', None)
            self.browser_manager = BrowserManager(headless=headless, proxy=proxy)
            self.driver = self.browser_manager.create_driver()

            url = self.config.general['questionnaire_url']
            fill_times = self.config.general['fill_times']

            self._log(f"任务开始: 目标 {fill_times} 份")
            self._success_count = 0
            self._fail_count = 0

            for i in range(fill_times):
                if self.stop_event.is_set():
                    self._log("用户中止任务")
                    break
                
                self._captcha_wait_event.wait()
                
                if self.stop_event.is_set():
                    self._log("用户中止任务")
                    break

                self._update_status(f"正在处理第 {i+1}/{fill_times} 份...")
                self._update_progress(i, fill_times)
                
                success = False
                for retry in range(self._retry_count):
                    if self.stop_event.is_set():
                        break
                    try:
                        self._process_one_questionnaire(i+1)
                        success = True
                        break
                    except CaptchaEncounteredError:
                        self._log("⚠️ 检测到验证码！请手动完成验证后点击'继续'按钮")
                        self._update_status("等待验证码处理...")
                        self._captcha_wait_event.clear()
                        self._captcha_wait_event.wait()
                        if retry < self._retry_count - 1:
                            self._log("重试中...")
                            continue
                        else:
                            raise
                    except PageLoadError as e:
                        self._log(f"❌ 页面加载失败: {e}", "ERROR")
                        if retry < self._retry_count - 1:
                            wait_time = (retry + 1) * 5
                            self._log(f"等待 {wait_time} 秒后重试...")
                            time.sleep(wait_time)
                        continue
                    except WebDriverException as e:
                        self._log(f"❌ 浏览器错误: {e}", "ERROR")
                        if retry < self._retry_count - 1:
                            self._log("尝试重新初始化浏览器...")
                            try:
                                if self.driver:
                                    self.driver.quit()
                                self.driver = self.browser_manager.create_driver()
                            except Exception:
                                pass
                        continue
                    except Exception as e:
                        self._log(f"❌ 第 {i+1} 份失败: {str(e)}", "ERROR")
                        if retry < self._retry_count - 1:
                            time.sleep(2)
                            continue

                if success:
                    self._success_count += 1
                    self._log(f"✅ 第 {i+1} 份完成")
                else:
                    self._fail_count += 1
                    self._log(f"❌ 第 {i+1} 份失败（已重试 {self._retry_count} 次）", "ERROR")

                if i < fill_times - 1 and not self.stop_event.is_set():
                    interval = self.config.general.get('interval_seconds', 3)
                    jitter = random.uniform(0, 2)
                    actual_interval = interval + jitter
                    self._log(f"等待 {actual_interval:.1f} 秒...")
                    time.sleep(actual_interval)

            self._update_progress(fill_times, fill_times)
            self._update_status(f"任务结束: 成功 {self._success_count}/{fill_times}, 失败 {self._fail_count}")
            self._log(f"📊 任务统计: 成功 {self._success_count} 份, 失败 {self._fail_count} 份")

        except BrowserInitError as e:
            self._log(f"❌ 浏览器初始化失败: {e}", "ERROR")
            self._update_status("浏览器初始化失败")
        except Exception as e:
            self._log(f"❌ 严重错误: {str(e)}", "ERROR")
            self._update_status("发生错误，任务停止")
        finally:
            self._cleanup()

    def _cleanup(self):
        """清理资源"""
        if self.driver:
            try:
                self.driver.quit()
                self._log("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器时出错: {e}")
            finally:
                self.driver = None

    def _process_one_questionnaire(self, index: int):
        """
        处理单份问卷的完整流程

        参数说明:
            index: 当前是第几份问卷（用于日志显示）
        """
        url = self.config.general['questionnaire_url']
        self.driver.get(url)

        page_timeout = self.config.general.get('page_timeout', 30)
        try:
            WebDriverWait(self.driver, page_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['question_page']['question_container']))
            )
        except TimeoutException:
            raise PageLoadError(f"页面加载超时（{page_timeout}秒），请检查网络或链接")

        if self._check_captcha():
            raise CaptchaEncounteredError()

        questions = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['question_page']['question_container'])
        
        if not questions:
            self._log("⚠️ 未检测到任何题目，可能页面结构已变化", "WARNING")

        for q_idx, q_element in enumerate(questions):
            if self.stop_event.is_set():
                return

            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", q_element)
                time.sleep(random.uniform(0.3, 0.8))
            except Exception:
                pass

            q_type = self._identify_question_type(q_element)
            q_num = q_idx + 1

            try:
                if q_type == 'single':
                    self.strategies['single'].execute(q_element, selectors=self.selectors)
                elif q_type == 'multiple':
                    self.strategies['multiple'].execute(q_element, selectors=self.selectors)
                elif q_type == 'blank':
                    self.strategies['blank'].execute(q_element, question_number=q_num, selectors=self.selectors)
                elif q_type == 'dropdown':
                    self.strategies['dropdown'].execute(q_element, selectors=self.selectors)
                else:
                    self._log(f"⚠️ 题目 {q_num}: 未知题型，跳过", "WARNING")
            except Exception as e:
                self._log(f"⚠️ 题目 {q_num} 处理出错: {e}", "WARNING")

        if self.config.general.get('auto_submit', True):
            self._submit_questionnaire()

    def _submit_questionnaire(self):
        """提交问卷并验证"""
        try:
            submit_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors['question_page']['submit_button']))
            )
            submit_btn.click()
            self._log("已点击提交按钮")
            
            time.sleep(2)
            
            success_indicator = self.selectors['question_page'].get('success_indicator')
            if success_indicator:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, success_indicator))
                    )
                    self._log("✅ 提交成功确认")
                except TimeoutException:
                    current_url = self.driver.current_url
                    if 'success' in current_url.lower() or 'complete' in current_url.lower():
                        self._log("✅ 提交成功（通过URL确认）")
                    else:
                        self._log("⚠️ 无法确认提交状态，请手动检查", "WARNING")
                        
        except TimeoutException:
            raise ElementNotFound("提交按钮未找到或不可点击")
        except Exception as e:
            raise TaskStarError(f"提交失败: {e}")

    def _check_captcha(self) -> bool:
        """
        检测是否出现验证码

        返回值:
            True: 检测到验证码
            False: 未检测到验证码
        """
        captcha_sel = self.selectors['question_page'].get('captcha_detection')
        if not captcha_sel:
            return False
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, captcha_sel)
            return el.is_displayed()
        except NoSuchElementException:
            return False

    def _identify_question_type(self, element) -> str:
        """
        识别题目类型

        参数说明:
            element: 题目的WebElement对象

        返回值:
            'single': 单选题
            'multiple': 多选题
            'blank': 填空题
            'dropdown': 下拉选择题
            'unknown': 未知题型
        """
        sp = self.selectors['question_page']

        if element.find_elements(By.CSS_SELECTOR, sp['single_choice']['option']):
            return 'single'

        if element.find_elements(By.CSS_SELECTOR, sp['multiple_choice']['option']):
            return 'multiple'
        
        dropdown_sel = sp.get('dropdown', {}).get('select', 'select')
        if element.find_elements(By.CSS_SELECTOR, dropdown_sel):
            return 'dropdown'

        if element.find_elements(By.CSS_SELECTOR, sp['fill_blank']['input']):
            return 'blank'

        return 'unknown'

    def stop(self):
        """
        停止当前任务
        设置停止事件标志，让run()方法退出循环
        """
        self.stop_event.set()
        self._captcha_wait_event.set()

    def resume_after_captcha(self):
        """
        在验证码处理后继续执行
        """
        self._captcha_wait_event.set()
        self._log("继续执行...")

    def wait_for_captcha(self, timeout: int = None):
        """
        等待验证码处理
        
        参数:
            timeout: 超时时间（秒），None表示无限等待
        """
        if timeout:
            self._captcha_wait_event.wait(timeout=timeout)
        else:
            self._captcha_wait_event.wait()

    @property
    def statistics(self) -> Dict[str, int]:
        """获取任务统计信息"""
        return {
            'success': self._success_count,
            'fail': self._fail_count,
            'total': self._success_count + self._fail_count
        }
