import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from .base import BaseStrategy


class DropdownStrategy(BaseStrategy):
    """
    下拉选择题策略：从下拉框中随机选择一个选项

    功能说明:
        识别页面中的 select 元素，随机选择一个非默认选项。
        支持单选和多选下拉框。
    """

    def execute(self, element, **kwargs):
        """
        执行下拉选择题填写策略

        参数说明:
            element: Selenium WebElement对象，代表题目容器
            **kwargs: 其他可选参数，例如:
                - selectors: CSS选择器字典
                - exclude_first: 是否排除第一个选项（通常是"请选择"之类的占位符）
        """
        selectors = kwargs.get('selectors', {})
        exclude_first = kwargs.get('exclude_first', True)
        
        dropdown_sel = "select"
        if selectors and 'question_page' in selectors:
            custom_selector = selectors['question_page'].get('dropdown', {}).get('select')
            if custom_selector:
                dropdown_sel = custom_selector

        dropdowns = element.find_elements(By.CSS_SELECTOR, dropdown_sel)

        if not dropdowns:
            print(f"[下拉选择题策略] 警告: 未找到下拉选择框")
            return

        for dropdown in dropdowns:
            try:
                select = Select(dropdown)
                options = select.options
                
                if not options:
                    continue
                
                if exclude_first and len(options) > 1:
                    options = options[1:]
                
                if options:
                    chosen_option = random.choice(options)
                    select.select_by_visible_text(chosen_option.text)
                    
            except NoSuchElementException:
                print(f"[下拉选择题策略] 警告: 下拉框选项未找到")
            except Exception as e:
                print(f"[下拉选择题策略] 错误: {e}")
