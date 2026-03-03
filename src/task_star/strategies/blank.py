import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base import BaseStrategy


class FillBlankStrategy(BaseStrategy):
    """
    填空题策略：从答案池中随机选择答案填入

    功能说明:
        根据题号从预配置的答案池中随机选择一个答案，
        自动填入填空题的输入框中。
    """

    def __init__(self, answer_pool: dict):
        """
        初始化填空题策略

        参数说明:
            answer_pool: 字典，键为题号，值为答案列表
                        格式: {题号1: ["答案1", "答案2", "答案3"], 题号2: [...]}
                        示例: {1: ["张三", "李四", "王五"], 2: ["计算机学院", "软件学院"]}

        配置说明:
            - 题号从 1 开始，对应问卷中的实际题号
            - 答案列表至少包含一个答案
            - 程序会从列表中随机选择一个答案填入
        """
        self.answer_pool = answer_pool

    def execute(self, element, question_number=None, **kwargs):
        """
        执行填空题填写策略

        参数说明:
            element: Selenium WebElement对象，代表题目容器
            question_number: 题号（必填），用于从答案池中查找对应的答案列表
                             注意: 这是问卷中的实际题号，从1开始
            **kwargs: 其他可选参数，例如:
                - selectors: CSS选择器字典

        处理流程:
            1. 验证题号是否传入
            2. 根据题号从答案池获取答案列表
            3. 验证答案列表是否为空
            4. 随机选择一个答案
            5. 查找输入框（可能是 input[type='text'] 或 textarea）
            6. 清空输入框并填入答案
            7. 模拟 TAB 键，模拟人类完成输入后的操作

        注意事项:
            - 如果题号未提供或答案池中没有对应题号，该填空题会被跳过
            - 建议为每个填空题配置多个答案，增加随机性
        """
        # 1. 验证题号是否传入
        if question_number is None:
            print(f"[填空题策略] 警告: 题号参数缺失，无法查找答案池，跳过该题")
            return

        # 2. 根据题号从答案池获取答案列表
        answers = self.answer_pool.get(question_number, [])

        # 3. 验证答案列表是否为空
        if not answers:
            print(f"[填空题策略] 警告: 题号 {question_number} 没有配置答案池，跳过该题")
            print(f"[填空题策略] 提示: 请在 config/config.yaml 的 fill_blanks 中添加该题号")
            return

        # 4. 随机选择一个答案
        chosen_answer = random.choice(answers)

        # 5. 查找输入框
        #    问卷星的填空题通常使用 input[type='text'] 或 textarea
        #    可以从自定义选择器中获取更精确的选择器
        selectors = kwargs.get('selectors', {})
        input_selector = "input[type='text'], textarea"

        if selectors and 'question_page' in selectors:
            # 优先使用配置文件中的选择器
            custom_selector = selectors['question_page']['fill_blank'].get('input')
            if custom_selector:
                input_selector = custom_selector

        # 查找输入框元素
        input_boxes = element.find_elements(By.CSS_SELECTOR, input_selector)

        if not input_boxes:
            print(f"[填空题策略] 警告: 题号 {question_number} 未找到输入框，跳过该题")
            return

        # 6. 填入答案（选择第一个找到的输入框）
        input_box = input_boxes[0]
        input_box.clear()  # 清空输入框中原有的内容
        input_box.send_keys(chosen_answer)  # 输入答案

        # 7. 模拟 TAB 键
        #    这会触发可能的输入验证，并移动焦点到下一个元素
        #    模拟人类完成输入后按 TAB 键的习惯行为
        input_box.send_keys(Keys.TAB)

        # 可选: 添加短暂延迟，模拟人类输入速度
        import time
        time.sleep(0.1) 
