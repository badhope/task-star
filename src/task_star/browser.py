from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException
from .utils import logger
from .exceptions import BrowserInitError


class BrowserManager:
    """
    浏览器管理器

    功能说明:
        负责 Chrome 浏览器的创建、配置和管理
        支持有界面和无界面（headless）两种模式
    """

    def __init__(self, headless: bool = False, proxy: Optional[str] = None, 
                 user_agent: Optional[str] = None, window_size: tuple = (1920, 1080)):
        """
        初始化浏览器管理器

        参数说明:
            headless: 是否使用无头模式
                    True: 后台运行，不显示浏览器窗口
                    False: 显示浏览器窗口，方便调试和观察
            proxy: 代理服务器地址，格式为 "host:port" 或 "http://host:port"
            user_agent: 自定义用户代理字符串
            window_size: 窗口大小，默认为 (1920, 1080)
        """
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent
        self.window_size = window_size
        self.driver = None

    def create_driver(self, timeout: int = 30):
        """
        创建并配置 Chrome 浏览器驱动

        参数:
            timeout: 页面加载超时时间（秒）

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
            options = Options()

            if self.headless:
                options.add_argument("--headless=new")
            else:
                options.add_argument("--start-maximized")

            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            if self.proxy:
                proxy_addr = self.proxy.replace("http://", "").replace("https://", "")
                options.add_argument(f"--proxy-server={proxy_addr}")
                logger.info(f"使用代理: {proxy_addr}")

            default_ua = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
            user_agent = self.user_agent or default_ua
            options.add_argument(f"user-agent={user_agent}")

            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            options.add_experimental_option("prefs", prefs)

            try:
                service = Service(ChromeDriverManager().install())
            except Exception as e:
                logger.warning(f"自动下载 ChromeDriver 失败: {e}，尝试使用系统路径")
                service = Service()

            try:
                self.driver = webdriver.Chrome(service=service, options=options)
            except SessionNotCreatedException as e:
                error_msg = str(e)
                if "version" in error_msg.lower():
                    raise BrowserInitError(
                        f"ChromeDriver 版本不匹配，请确保 Chrome 浏览器已更新。\n"
                        f"错误详情: {error_msg}\n"
                        f"建议: 运行 'pip install --upgrade webdriver-manager' 更新驱动管理器"
                    )
                raise BrowserInitError(f"浏览器会话创建失败: {error_msg}")

            if not self.headless:
                try:
                    self.driver.maximize_window()
                except Exception:
                    pass

            self.driver.set_page_load_timeout(timeout)
            self.driver.implicitly_wait(10)

            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })

            logger.info("浏览器驱动创建成功")
            return self.driver

        except BrowserInitError:
            raise
        except WebDriverException as e:
            error_msg = str(e)
            if "cannot find Chrome binary" in error_msg.lower():
                raise BrowserInitError(
                    "未找到 Chrome 浏览器，请确保已安装 Chrome。\n"
                    "下载地址: https://www.google.com/chrome/"
                )
            elif "connection refused" in error_msg.lower():
                raise BrowserInitError(
                    "ChromeDriver 连接被拒绝，可能端口被占用。\n"
                    "建议: 关闭其他浏览器实例后重试"
                )
            else:
                raise BrowserInitError(f"浏览器初始化失败: {error_msg}")
        except Exception as e:
            logger.error(f"创建浏览器驱动失败：{e}")
            raise BrowserInitError(f"浏览器初始化失败: {str(e)}")

    def quit(self):
        """
        关闭浏览器并释放资源

        注意事项:
            - 调用此方法后，driver 对象将无法继续使用
            - 建议在 finally 块中调用，确保资源释放
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器时出错: {e}")
            finally:
                self.driver = None

    def restart(self, timeout: int = 30):
        """
        重启浏览器
        
        参数:
            timeout: 页面加载超时时间（秒）
        """
        self.quit()
        return self.create_driver(timeout=timeout)

    def take_screenshot(self, filepath: str) -> bool:
        """
        截取当前页面截图
        
        参数:
            filepath: 截图保存路径
            
        返回:
            bool: 是否成功
        """
        if self.driver:
            try:
                self.driver.save_screenshot(filepath)
                logger.info(f"截图已保存: {filepath}")
                return True
            except Exception as e:
                logger.error(f"截图失败: {e}")
                return False
        return False

    def get_current_url(self) -> Optional[str]:
        """获取当前页面URL"""
        if self.driver:
            try:
                return self.driver.current_url
            except Exception:
                return None
        return None

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
        return False
