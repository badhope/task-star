import random
from selenium.webdriver.common.by import By
from .base import BaseStrategy


class SingleChoiceStrategy(BaseStrategy):
    """
    单选题策略：从所有选项中随机选择一个

    功能说明:
        在题目容器内查找所有单选按钮（radio button），
        随机选择一个进行点击，实现单选题的自动填写。
    """

    def execute(self, element, **kwargs):
        """
        执行单选题填写策略

        参数说明:
            element: Selenium WebElement对象，代表题目容器
            **kwargs: 其他可选参数，例如:
                - selectors: CSS选择器字典 (用于自定义元素查找方式)

        处理流程:
            1. 在题目容器内查找所有单选按钮 (input[type='radio'])
            2. 如果没找到，尝试使用备用选择器 (div.radio-div)
            3. 从可用的单选按钮中随机选择一个
            4. 点击选中的按钮
        """
        # 1. 在题目容器内查找所有单选按钮
        #    问卷星通常使用 input[type='radio'] 作为单选按钮
        #    注意: 问卷星的DOM结构可能会更新，需要根据实际情况调整
        radio_buttons = element.find_elements(By.CSS_SELECTOR, "input[type='radio']")

        # 2. 如果没有找到单选按钮，尝试使用备用选择器
        #    问卷星有时会用 div 元素模拟单选按钮效果
        #    这里的选择器需要根据实际的HTML结构调整
        if not radio_buttons:
            # 尝试查找可能的备用选择器
            # 可以从 kwargs 中获取自定义选择器
            selectors = kwargs.get('selectors', {})
            if selectors and 'question_page' in selectors:
                alternative_selector = selectors['question_page']['single_choice'].get('alternative')
                if alternative_selector:
                    radio_buttons = element.find_elements(By.CSS_SELECTOR, alternative_selector)

            # 如果还是没有找到，再尝试硬编码的备用选择器
            if not radio_buttons:
                radio_buttons = element.find_elements(By.CSS_SELECTOR, "div.radio-div")

        # 3. 执行选择操作
        if radio_buttons:
            # 从所有单选按钮中随机选择一个
            chosen_radio = random.choice(radio_buttons)
            # 点击选中的按钮
            chosen_radio.click()
        else:
            # 如果还是没找到单选按钮，输出警告信息
            # 可能原因:
            #   1. 题目类型判断错误（可能是多选题或填空题）
            #   2. 问卷星更新了DOM结构
            #   3. 页面加载未完成
            print(f"[单选题策略] 警告: 未找到单选按钮，请检查题目类型或DOM结构")
