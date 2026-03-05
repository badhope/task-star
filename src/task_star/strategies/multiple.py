import random
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from .base import BaseStrategy


class MultipleChoiceStrategy(BaseStrategy):
    """
    多选题策略：随机选择指定范围内的选项数量

    功能说明:
        从所有选项中随机选择一定数量的选项，选择的数量在
        min_select 和 max_select 之间，模拟人类的随机选择行为。
    """

    def __init__(self, min_select: int = 2, max_select: int = 3):
        """
        初始化多选题策略

        参数说明:
            min_select: 最少选择项数，默认为2
            max_select: 最多选择项数，默认为3
                        如果设为 -1 表示不限制（选择所有选项）
        """
        self.min_select = min_select
        self.max_select = max_select

    def execute(self, element: WebElement, **kwargs):
        """
        执行多选题填写策略

        参数说明:
            element: Selenium WebElement对象，代表题目容器
            **kwargs: 其他可选参数，例如:
                - selectors: CSS选择器字典
        """
        min_sel = kwargs.get('min_select', self.min_select)
        max_sel = kwargs.get('max_select', self.max_select)
        selectors = kwargs.get('selectors', {})

        checkboxes = element.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")

        if not checkboxes:
            if selectors and 'question_page' in selectors:
                alternative_selector = selectors['question_page']['multiple_choice'].get('alternative')
                if alternative_selector:
                    checkboxes = element.find_elements(By.CSS_SELECTOR, alternative_selector)

            if not checkboxes:
                checkboxes = element.find_elements(By.CSS_SELECTOR, "div.checkbox-div, div.ui-checkbox")

        if checkboxes:
            visible_checkboxes = [c for c in checkboxes if c.is_displayed()]
            
            if not visible_checkboxes:
                visible_checkboxes = checkboxes
            
            total_options = len(visible_checkboxes)

            max_sel = min(max_sel, total_options) if max_sel != -1 else total_options
            min_sel = min(min_sel, max_sel)

            if max_sel == -1:
                num_to_select = total_options
            else:
                if max_sel <= min_sel:
                    num_to_select = min_sel
                else:
                    num_to_select = random.randint(min_sel, max_sel)

            chosen_checkboxes = random.sample(visible_checkboxes, num_to_select)
            for checkbox in chosen_checkboxes:
                try:
                    checkbox.click()
                except Exception:
                    try:
                        parent = checkbox.find_element(By.XPATH, "..")
                        parent.click()
                    except Exception:
                        pass
        else:
            print(f"[多选题策略] 警告: 未找到复选框，请检查题目类型或DOM结构")
