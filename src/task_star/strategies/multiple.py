import random
from selenium.webdriver.common.by import By
from .base import BaseStrategy


class MultipleChoiceStrategy(BaseStrategy):
    """
    多选题策略：随机选择指定范围内的选项数量

    功能说明:
        从所有选项中随机选择一定数量的选项，选择的数量在
        min_select 和 max_select 之间，模拟人类的随机选择行为。
    """

    def __init__(self, min_select=2, max_select=3):
        """
        初始化多选题策略

        参数说明:
            min_select: 最少选择项数，默认为2
            max_select: 最多选择项数，默认为3
                        如果设为 -1 表示不限制（选择所有选项）

        注意事项:
            - min_select 必须小于等于 max_select
            - 如果选项总数少于 max_select，则最多选择所有选项
        """
        self.min_select = min_select
        self.max_select = max_select

    def execute(self, element, **kwargs):
        """
        执行多选题填写策略

        参数说明:
            element: Selenium WebElement对象，代表题目容器
            **kwargs: 其他可选参数，例如:
                - selectors: CSS选择器字典

        处理流程:
            1. 从 kwargs 或配置中获取最小/最大选择数
            2. 在题目容器内查找所有复选框 (input[type='checkbox'])
            3. 如果没找到，尝试使用备用选择器
            4. 验证选择数量的有效性
            5. 随机决定要选择的数量
            6. 随机选择对应数量的复选框并点击
        """
        # 1. 获取最小/最大选择数
        #    优先使用传入的参数，否则使用初始化时的默认值
        min_sel = kwargs.get('min_select', self.min_select)
        max_sel = kwargs.get('max_select', self.max_select)

        # 2. 在题目容器内查找所有复选框
        #    问卷星通常使用 input[type='checkbox'] 作为复选框
        checkboxes = element.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")

        # 3. 如果没有找到复选框，尝试使用备用选择器
        if not checkboxes:
            # 尝试从自定义选择器中获取备用选择器
            selectors = kwargs.get('selectors', {})
            if selectors and 'question_page' in selectors:
                alternative_selector = selectors['question_page']['multiple_choice'].get('alternative')
                if alternative_selector:
                    checkboxes = element.find_elements(By.CSS_SELECTOR, alternative_selector)

            # 硬编码的备用选择器
            if not checkboxes:
                checkboxes = element.find_elements(By.CSS_SELECTOR, "div.checkbox-div")

        # 4. 执行选择操作
        if checkboxes:
            total_options = len(checkboxes)

            # 验证并调整最大选择数，不能超过总选项数
            # 例如: 题目只有4个选项，但配置要求最多选5个，则最多只能选4个
            max_sel = min(max_sel, total_options)

            # 验证最小选择数不能超过最大选择数
            # 例如: 最少选3个，最多选2个，这是不合理的，调整为都选2个
            min_sel = min(min_sel, max_sel)

            # 特殊处理: 如果 max_select 为 -1，表示选择所有选项
            if max_sel == -1:
                num_to_select = total_options
            else:
                # 5. 随机决定要选择的数量
                #    在 min_sel 和 max_sel 之间随机选择一个数字
                if max_sel <= min_sel:
                    num_to_select = min_sel
                else:
                    num_to_select = random.randint(min_sel, max_sel)

            # 6. 从所有复选框中随机选取指定数量，并逐个点击
            #    random.sample 保证不重复选择
            chosen_checkboxes = random.sample(checkboxes, num_to_select)
            for checkbox in chosen_checkboxes:
                checkbox.click()
        else:
            # 如果没找到复选框，输出警告信息
            print(f"[多选题策略] 警告: 未找到复选框，请检查题目类型或DOM结构")
