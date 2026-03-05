import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from typing import Dict, List, Optional
from .base import BaseStrategy


class FillBlankStrategy(BaseStrategy):
    """
    填空题策略：从答案池中随机选择答案填入

    功能说明:
        根据题号从预配置的答案池中随机选择一个答案，
        自动填入填空题的输入框中。
    """

    def __init__(self, answer_pool: Optional[Dict[int, List[str]]] = None):
        """
        初始化填空题策略

        参数说明:
            answer_pool: 字典，键为题号，值为答案列表
                        格式: {题号1: ["答案1", "答案2", "答案3"], 题号2: [...]}
        """
        self.answer_pool = answer_pool or {}

    def execute(self, element: WebElement, question_number: Optional[int] = None, **kwargs):
        """
        执行填空题填写策略

        参数说明:
            element: Selenium WebElement对象，代表题目容器
            question_number: 题号（必填），用于从答案池中查找对应的答案列表
            **kwargs: 其他可选参数，例如:
                - selectors: CSS选择器字典
        """
        if question_number is None:
            print(f"[填空题策略] 警告: 题号参数缺失，无法查找答案池，跳过该题")
            return

        answers = self.answer_pool.get(question_number, [])

        if not answers:
            print(f"[填空题策略] 警告: 题号 {question_number} 没有配置答案池，跳过该题")
            return

        chosen_answer = random.choice(answers)

        selectors = kwargs.get('selectors', {})
        input_selector = "input[type='text'], textarea, input.u-input"

        if selectors and 'question_page' in selectors:
            custom_selector = selectors['question_page']['fill_blank'].get('input')
            if custom_selector:
                input_selector = custom_selector

        input_boxes = element.find_elements(By.CSS_SELECTOR, input_selector)

        if not input_boxes:
            input_boxes = element.find_elements(By.CSS_SELECTOR, "input:not([type='radio']):not([type='checkbox']):not([type='submit']), textarea")

        if not input_boxes:
            print(f"[填空题策略] 警告: 题号 {question_number} 未找到输入框，跳过该题")
            return

        visible_inputs = [i for i in input_boxes if i.is_displayed()]
        if not visible_inputs:
            visible_inputs = input_boxes
        
        input_box = visible_inputs[0]
        
        try:
            input_box.clear()
            time.sleep(0.1)
            
            for char in chosen_answer:
                input_box.send_keys(char)
                time.sleep(random.uniform(0.01, 0.05))
            
            input_box.send_keys(Keys.TAB)
            
        except Exception as e:
            print(f"[填空题策略] 错误: 填入答案失败 - {e}")
            try:
                element.execute_script("arguments[0].value = arguments[1];", input_box, chosen_answer)
            except Exception:
                pass

        time.sleep(0.1)
