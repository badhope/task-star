from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from .utils import logger
from .exceptions import BrowserInitError


class BrowserManager:
    """
    浏览器管理器

    功能说明:
        负责 Chrome 浏览器的创建、配置和管理
        支持有界面和无界面（headless）两种模式
    """

    def __init__(self, headless=False):
        """
        初始化浏览器管理器

        参数说明:
            headless: 是否使用无头模式
                    True: 后台运行，不显示浏览器窗口
                    False: 显示浏览器窗口，方便调试和观察

        使用场景:
            - 调试阶段建议设为 False，可以看到实际操作过程
            - 批量任务可以设为 True，节省系统资源
        """
        self.headless = headless
        self.driver = None  # Selenium WebDriver 对象

    def create_driver(self):
        """
        创建并配置 Chrome 浏览器驱动

        返回值:
            WebDriver: 配置好的浏览器驱动对象

        抛出异常:
            BrowserInitError: 当浏览器创建失败时抛出

        浏览器配置说明:
            --no-sandbox: 在某些Linux环境下需要，禁用沙箱模式
            --disable-dev-shm-usage: 解决/dev/shm空间不足的问题
            --disable-gpu: 在无界面模式下禁用GPU加速
            --window-size=1920,1080: 设置窗口大小，模拟常见分辨率
            --disable-notifications: 禁用浏览器通知
            --disable-extensions: 禁用扩展，提高启动速度
        """
        try:
            # 1. 创建浏览器选项对象
            options = Options()

            # 2. 配置无头模式（后台运行）
            if self.headless:
                # 新版本的Chrome使用 --headless=new 作为无头模式
                options.add_argument("--headless=new")
            else:
                # 有界面模式下，添加一些优化选项
                options.add_argument("--start-maximized")

            # 3. 设置浏览器优化选项
            #    这些选项可以提高稳定性和兼容性
            options.add_argument("--no-sandbox")  # 禁用沙箱（在服务器上通常需要）
            options.add_argument("--disable-dev-shm-usage")  # 解决内存不足问题
            options.add_argument("--disable-gpu")  # 禁用GPU加速
            options.add_argument("--window-size=1920,1080")  # 设置窗口大小
            options.add_argument("--disable-notifications")  # 禁用通知弹窗
            options.add_argument("--disable-extensions")  # 禁用扩展
            options.add_argument("--disable-infobars")  # 禁用信息栏
            options.add_argument("--disable-blink-features=AutomationControlled")  # 隐藏自动化特征

            # 4. 设置用户代理，模拟真实浏览器
            #    这可以减少被网站识别为机器人的风险
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )

            # 5. 自动安装匹配的 ChromeDriver
            #    ChromeDriverManager 会自动检测 Chrome 版本并下载对应驱动
            service = Service(ChromeDriverManager().install())

            # 6. 创建 WebDriver 实例
            self.driver = webdriver.Chrome(service=service, options=options)

            # 7. 最大化窗口（仅在非无头模式下有效）
            if not self.headless:
                self.driver.maximize_window()

            # 8. 设置隐式等待时间
            #    在查找元素时，如果元素不存在，最多等待10秒
            self.driver.implicitly_wait(10)

            logger.info("浏览器驱动创建成功")
            return self.driver

        except Exception as e:
            # 捕获并记录创建过程中的错误
            logger.error(f"创建浏览器驱动失败：{e}")
            # 抛出自定义异常，方便上层处理
            raise BrowserInitError(f"浏览器初始化失败: {str(e)}")

    def quit(self):
        """
        关闭浏览器并释放资源

        注意事项:
            - 调用此方法后，driver 对象将无法继续使用
            - 建议在 finally 块中调用，确保资源释放
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("浏览器已关闭")

    def __enter__(self):
        """
        支持上下文管理器协议 (with 语句)
        """
        self.create_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文时自动关闭浏览器
        """
        self.quit()
