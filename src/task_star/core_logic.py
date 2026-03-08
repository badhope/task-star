"""问卷填写核心逻辑"""

import time
import random
from typing import Optional, Callable, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .config import config
from .browser import BrowserManager
from .exceptions import ConfigError, BrowserInitError, PageLoadError, CaptchaRequired
from .utils import logger


class QuestionnaireFiller:
    """问卷填写器"""

    def __init__(self, status_callback: Optional[Callable] = None,
                 log_callback: Optional[Callable] = None,
                 progress_callback: Optional[Callable] = None,
                 stop_event: Optional[Any] = None):
        if config is None:
            raise ConfigError("配置加载失败，请检查 config/config.yaml")

        self.config = config
        self.status_callback = status_callback
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        
        class SimpleEvent:
            def __init__(self):
                self._flag = True
            def is_set(self): return self._flag
            def set(self): self._flag = True
            def clear(self): self._flag = False
            def wait(self): pass
        
        self.stop_event = stop_event or SimpleEvent()
        self._captcha_wait_event = SimpleEvent()
        self.selectors = self._load_selectors()
        
        self._success_count = 0
        self._fail_count = 0
        self._retry_count = self.config.general.get('retry_count', 3)
        self.driver = None
        self.browser_manager = None

    def _load_selectors(self) -> Dict[str, Any]:
        """加载选择器配置"""
        from pathlib import Path
        import yaml
        
        sel_path = Path(__file__).parent.parent.parent / "config" / "selectors.yaml"
        if not sel_path.exists():
            logger.warning("selectors.yaml 不存在，使用默认选择器")
            return self._get_default_selectors()
        
        try:
            with open(sel_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or self._get_default_selectors()
        except Exception as e:
            logger.error(f"加载选择器失败：{e}")
            return self._get_default_selectors()

    def _get_default_selectors(self) -> Dict[str, Any]:
        """默认选择器"""
        return {
            'question_page': {
                'question_container': "div.field",
                'submit_button': "input#submit_button, button#submit_button",
                'single_choice': {'option': "input[type='radio']"},
                'multiple_choice': {'option': "input[type='checkbox']"},
                'fill_blank': {'input': "input[type='text'], textarea"},
                'dropdown': {'select': "select"},
                'captcha_detection': "div#divCaptcha, div.geetest_panel",
                'success_indicator': "div.success, div#success_page"
            }
        }

    def _log(self, msg: str, level: str = "INFO"):
        """记录日志"""
        if self.log_callback:
            try:
                self.log_callback(msg)
            except Exception:
                pass
        
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(msg)

    def _update_status(self, msg: str):
        """更新状态"""
        if self.status_callback:
            try:
                self.status_callback(msg)
            except Exception:
                pass
        logger.info(msg)

    def _update_progress(self, current: int, total: int):
        """更新进度"""
        if self.progress_callback:
            try:
                self.progress_callback(current, total)
            except Exception:
                pass

    def run(self):
        """主运行逻辑"""
        try:
            self._update_status("正在初始化浏览器...")
            
            headless = self.config.general.get('headless', False)
            proxy = self.config.general.get('proxy', None)
            self.browser_manager = BrowserManager(headless=headless, proxy=proxy)
            self.driver = self.browser_manager.create_driver()

            url = self.config.general['questionnaire_url']
            fill_times = self.config.general['fill_times']

            self._log(f"任务开始：目标 {fill_times} 份")
            self._success_count = 0
            self._fail_count = 0

            for i in range(fill_times):
                if self.stop_event.is_set():
                    self._log("用户中止任务")
                    break
                
                self._captcha_wait_event.wait()
                
                if self.stop_event.is_set():
                    break

                self._update_status(f"正在处理第 {i+1}/{fill_times} 份...")
                self._update_progress(i, fill_times)
                
                success = False
                for retry in range(self._retry_count):
                    if self.stop_event.is_set():
                        break
                    try:
                        self._process_one_questionnaire(i + 1)
                        success = True
                        break
                    except CaptchaRequired:
                        self._log("⚠️ 检测到验证码！请手动完成后点击继续")
                        self._update_status("等待验证码处理...")
                        self._captcha_wait_event.clear()
                        self._captcha_wait_event.wait()
                        if retry < self._retry_count - 1:
                            self._log("重试中...")
                            continue
                        else:
                            raise
                    except PageLoadError as e:
                        self._log(f"❌ 页面加载失败：{e}", "ERROR")
                        if retry < self._retry_count - 1:
                            wait_time = (retry + 1) * 5
                            self._log(f"等待 {wait_time} 秒后重试...")
                            time.sleep(wait_time)
                        continue
                    except Exception as e:
                        self._log(f"❌ 第 {i+1} 份失败：{str(e)}", "ERROR")
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
            self._update_status(f"任务结束：成功 {self._success_count}/{fill_times}, 失败 {self._fail_count}")
            self._log(f"📊 任务统计：成功 {self._success_count} 份，失败 {self._fail_count} 份")

        except BrowserInitError as e:
            self._log(f"❌ 浏览器初始化失败：{e}", "ERROR")
            self._update_status("浏览器初始化失败")
        except Exception as e:
            self._log(f"❌ 严重错误：{str(e)}", "ERROR")
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
                logger.error(f"关闭浏览器失败：{e}")
            finally:
                self.driver = None

    def _process_one_questionnaire(self, index: int):
        """处理单份问卷"""
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
            raise CaptchaRequired()

        questions = self.driver.find_elements(By.CSS_SELECTOR, self.selectors['question_page']['question_container'])
        
        if not questions:
            self._log("⚠️ 未检测到任何题目", "WARNING")

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
                    self._handle_single_choice(q_element)
                elif q_type == 'multiple':
                    self._handle_multiple_choice(q_element)
                elif q_type == 'blank':
                    self._handle_blank(q_element, q_num)
                elif q_type == 'dropdown':
                    self._handle_dropdown(q_element)
                else:
                    self._log(f"⚠️ 题目 {q_num}: 未知题型，跳过", "WARNING")
            except Exception as e:
                self._log(f"⚠️ 题目 {q_num} 处理出错：{e}", "WARNING")

        if self.config.general.get('auto_submit', True):
            self._submit_questionnaire()

    def _handle_single_choice(self, element):
        """处理单选题"""
        radio_buttons = element.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        if not radio_buttons:
            radio_buttons = element.find_elements(By.CSS_SELECTOR, "div.radio-div, div.ui-radio")

        if not radio_buttons:
            return

        visible = [r for r in radio_buttons if r.is_displayed()]
        if not visible:
            visible = radio_buttons
            
        if visible:
            chosen = random.choice(visible)
            try:
                chosen.click()
            except Exception:
                try:
                    chosen.find_element(By.XPATH, "..").click()
                except Exception:
                    pass

    def _handle_multiple_choice(self, element):
        """处理多选题"""
        checkboxes = element.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        if not checkboxes:
            checkboxes = element.find_elements(By.CSS_SELECTOR, "div.checkbox-div, div.ui-checkbox")

        if not checkboxes:
            return

        visible = [c for c in checkboxes if c.is_displayed()]
        if not visible:
            visible = checkboxes
        
        total = len(visible)
        if total == 0:
            return
            
        mc_config = self.config.strategy.get('multi_choice', {})
        min_sel = mc_config.get('min_select', 2)
        max_sel = mc_config.get('max_select', 3)
        
        max_sel = min(max_sel, total) if max_sel != -1 else total
        min_sel = min(min_sel, max_sel)
        
        if max_sel <= min_sel:
            num_to_select = min_sel
        elif max_sel == -1:
            num_to_select = total
        else:
            num_to_select = random.randint(min_sel, max_sel)
        
        if num_to_select > total:
            num_to_select = total
        
        chosen = random.sample(visible, num_to_select)
        for cb in chosen:
            try:
                cb.click()
            except Exception:
                try:
                    cb.find_element(By.XPATH, "..").click()
                except Exception:
                    pass

    def _handle_blank(self, element, question_number: int):
        """处理填空题"""
        answers = self.config.strategy.get('fill_blanks', {}).get(question_number, [])
        if not answers:
            self._log(f"⚠️ 题号 {question_number} 未配置答案", "WARNING")
            return

        chosen_answer = random.choice(answers)
        input_boxes = element.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea, input.u-input")
        
        if not input_boxes:
            input_boxes = element.find_elements(By.CSS_SELECTOR, "input:not([type='radio']):not([type='checkbox']):not([type='submit']), textarea")

        if not input_boxes:
            self._log(f"❌ 题号 {question_number} 未找到输入框", "ERROR")
            return

        input_box = input_boxes[0]
        try:
            input_box.clear()
            time.sleep(0.05)
            input_box.send_keys(chosen_answer)
            input_box.send_keys(Keys.TAB)
        except Exception as e:
            self._log(f"❌ 填空失败：{e}", "ERROR")
            try:
                element.execute_script("arguments[0].value = arguments[1];", input_box, chosen_answer)
            except Exception:
                pass

    def _handle_dropdown(self, element):
        """处理下拉选择题"""
        dropdowns = element.find_elements(By.CSS_SELECTOR, "select")
        if not dropdowns:
            return
            
        for dropdown in dropdowns:
            try:
                select = Select(dropdown)
                options = select.options
                if len(options) > 1:
                    chosen = random.choice(options[1:])
                    select.select_by_visible_text(chosen.text)
                elif options:
                    select.select_by_index(0)
            except Exception as e:
                self._log(f"❌ 下拉题处理失败：{e}", "ERROR")

    def _identify_question_type(self, element) -> str:
        """识别题目类型"""
        sp = self.selectors['question_page']

        if element.find_elements(By.CSS_SELECTOR, sp['single_choice']['option']):
            return 'single'

        if element.find_elements(By.CSS_SELECTOR, sp['multiple_choice']['option']):
            return 'multiple'
        
        if element.find_elements(By.CSS_SELECTOR, sp.get('dropdown', {}).get('select', 'select')):
            return 'dropdown'

        if element.find_elements(By.CSS_SELECTOR, sp['fill_blank']['input']):
            return 'blank'

        return 'unknown'

    def _submit_questionnaire(self):
        """提交问卷"""
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
                        self._log("✅ 提交成功（通过 URL 确认）")
                    else:
                        self._log("⚠️ 无法确认提交状态", "WARNING")
                        
        except TimeoutException:
            raise TimeoutException("提交按钮未找到或不可点击")
        except Exception as e:
            raise Exception(f"提交失败：{e}")

    def _check_captcha(self) -> bool:
        """检测验证码"""
        captcha_sel = self.selectors['question_page'].get('captcha_detection')
        if not captcha_sel:
            return False
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, captcha_sel)
            return el.is_displayed()
        except NoSuchElementException:
            return False

    def stop(self):
        """停止任务"""
        self.stop_event.set()
        self._captcha_wait_event.set()

    def resume_after_captcha(self):
        """验证码处理后继续"""
        self._captcha_wait_event.set()
        self._log("继续执行...")

    @property
    def statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            'success': self._success_count,
            'fail': self._fail_count,
            'total': self._success_count + self._fail_count
        }
