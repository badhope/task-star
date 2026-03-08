"""浏览器管理器"""

from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException

from .utils import logger
from .exceptions import BrowserInitError


class BrowserManager:
    """浏览器管理器"""

    def __init__(self, headless: bool = False, proxy: Optional[str] = None):
        self.headless = headless
        self.proxy = proxy
        self.driver = None

    def create_driver(self, timeout: int = 30):
        """创建 Chrome 浏览器驱动"""
        try:
            options = Options()

            if self.headless:
                options.add_argument("--headless=new")
            else:
                options.add_argument("--start-maximized")

            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            if self.proxy:
                proxy_addr = self.proxy.replace("http://", "").replace("https://", "")
                options.add_argument(f"--proxy-server={proxy_addr}")
                logger.info(f"使用代理：{proxy_addr}")

            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            options.add_argument(f"user-agent={ua}")

            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            options.add_experimental_option("prefs", prefs)

            try:
                service = Service(ChromeDriverManager().install())
            except Exception as e:
                logger.warning(f"ChromeDriver 自动下载失败：{e}，使用系统路径")
                service = Service()

            try:
                self.driver = webdriver.Chrome(service=service, options=options)
            except SessionNotCreatedException as e:
                error_msg = str(e)
                if "version" in error_msg.lower():
                    raise BrowserInitError(
                        f"ChromeDriver 版本不匹配。\n"
                        f"错误：{error_msg}\n"
                        f"建议：1. 更新 Chrome 浏览器\n"
                        f"      2. 运行 'pip install --upgrade webdriver-manager'"
                    )
                raise BrowserInitError(f"浏览器创建失败：{error_msg}")
            except Exception as e:
                raise BrowserInitError(f"浏览器初始化失败：{e}")

            if not self.headless:
                try:
                    self.driver.maximize_window()
                except Exception:
                    pass

            self.driver.set_page_load_timeout(timeout)
            self.driver.implicitly_wait(10)

            try:
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                })
            except Exception:
                pass

            logger.info("浏览器驱动创建成功")
            return self.driver

        except BrowserInitError:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "cannot find chrome binary" in error_msg:
                raise BrowserInitError("未找到 Chrome 浏览器，请安装：https://www.google.com/chrome/")
            elif "connection refused" in error_msg:
                raise BrowserInitError("ChromeDriver 连接被拒绝，请关闭其他浏览器实例后重试")
            else:
                raise BrowserInitError(f"浏览器初始化失败：{e}")

    def quit(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器失败：{e}")
            finally:
                self.driver = None

    def __enter__(self):
        self.create_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
        return False
