import random
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from .base import BaseStrategy


class SingleChoiceStrategy(BaseStrategy):
    """
    单选题策略：从所有选项中随机选择一个

    功能说明:
        在题目容器内查找所有单选按钮（radio button），
        随机选择一个进行点击，实现单选题的自动填写。
    """

    def execute(self, element: WebElement, **kwargs):
        """
        执行单选题填写策略

        参数说明:
            element: Selenium WebElement对象，代表题目容器
            **kwargs: 其他可选参数，例如:
                - selectors: CSS选择器字典 (用于自定义元素查找方式)
        """
        selectors = kwargs.get('selectors', {})
        
        radio_buttons = element.find_elements(By.CSS_SELECTOR, "input[type='radio']")

        if not radio_buttons:
            if selectors and 'question_page' in selectors:
                alternative_selector = selectors['question_page']['single_choice'].get('alternative')
                if alternative_selector:
                    radio_buttons = element.find_elements(By.CSS_SELECTOR, alternative_selector)

            if not radio_buttons:
                radio_buttons = element.find_elements(By.CSS_SELECTOR, "div.radio-div, div.ui-radio")

        if radio_buttons:
            visible_radios = [r for r in radio_buttons if r.is_displayed()]
            if visible_radios:
                chosen_radio = random.choice(visible_radios)
                try:
                    chosen_radio.click()
                except Exception:
                    parent = chosen_radio.find_element(By.XPATH, "..")
                    parent.click()
            else:
                print(f"[单选题策略] 警告: 未找到可见的单选按钮")
        else:
            print(f"[单选题策略] 警告: 未找到单选按钮，请检查题目类型或DOM结构")
