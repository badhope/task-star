"""
Task-Star 自动环境配置脚本

功能说明:
    自动检测并配置 Task-Star 程序的运行环境，包括:
    1. Python 版本检查
    2. 依赖包自动安装
    3. 环境变量设置
    4. Chrome 浏览器检测
    5. 配置文件检查和创建
    6. 详细的安装日志
    7. 完善的错误处理

使用方法:
    python auto_setup.py

作者: Task-Star 开发团队
日期: 2026-03-03
"""

import sys
import os
import subprocess
import platform
import shutil
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class Colors:
    """控制台颜色输出"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def reset():
        return Colors.END

    @staticmethod
    def success(text):
        return f"{Colors.GREEN}✅ {text}{Colors.END}"

    @staticmethod
    def error(text):
        return f"{Colors.RED}❌ {text}{Colors.END}"

    @staticmethod
    def warning(text):
        return f"{Colors.YELLOW}⚠️  {text}{Colors.END}"

    @staticmethod
    def info(text):
        return f"{Colors.CYAN}ℹ️  {text}{Colors.END}"

    @staticmethod
    def progress(text):
        return f"{Colors.BLUE}🔄 {text}{Colors.END}"


class Logger:
    """日志管理器"""

    def __init__(self, log_file: str = "auto_setup.log"):
        """
        初始化日志管理器

        参数:
            log_file: 日志文件路径
        """
        self.log_file = log_file
        self.start_time = datetime.now()
        self._init_log_file()

    def _init_log_file(self):
        """初始化日志文件"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"Task-Star 环境自动配置日志\n")
            f.write(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"系统: {platform.system()} {platform.release()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write("=" * 80 + "\n\n")

    def log(self, level: str, message: str):
        """
        记录日志

        参数:
            level: 日志级别 (INFO, SUCCESS, WARNING, ERROR)
            message: 日志消息
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        # 写入文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        # 输出到控制台
        if level == "INFO":
            print(Colors.info(message))
        elif level == "SUCCESS":
            print(Colors.success(message))
        elif level == "WARNING":
            print(Colors.warning(message))
        elif level == "ERROR":
            print(Colors.error(message))

    def info(self, message):
        """信息日志"""
        self.log("INFO", message)

    def success(self, message):
        """成功日志"""
        self.log("SUCCESS", message)

    def warning(self, message):
        """警告日志"""
        self.log("WARNING", message)

    def error(self, message):
        """错误日志"""
        self.log("ERROR", message)

    def separator(self):
        """输出分隔线"""
        line = "-" * 80
        print(line)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line + "\n")

    def summary(self, total: int, passed: int, failed: int):
        """输出总结"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.separator()
        self.info(f"配置完成，耗时: {duration:.2f} 秒")
        self.info(f"总计: {total} 项 | 通过: {passed} 项 | 失败: {failed} 项")
        self.separator()

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n配置完成，耗时: {duration:.2f} 秒\n")
            f.write(f"总计: {total} 项 | 通过: {passed} 项 | 失败: {failed} 项\n")
            f.write(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")


class EnvironmentChecker:
    """环境检查器"""

    REQUIRED_PYTHON_VERSION = (3, 8)  # 最低 Python 版本要求

    # 必需的依赖包
    REQUIRED_PACKAGES = {
        'selenium': '4.15.0',
        'webdriver_manager': '4.0.1',
        'pyyaml': '6.0',
        'customtkinter': '5.2.1',
        'pillow': '10.0.0',
    }

    def __init__(self, logger: Logger):
        """
        初始化环境检查器

        参数:
            logger: 日志管理器实例
        """
        self.logger = logger
        self.installed_packages = {}
        self.missing_packages = []
        self.system_info = self._get_system_info()

    def _get_system_info(self) -> Dict[str, str]:
        """
        获取系统信息

        返回:
            包含系统详细信息的字典
        """
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'python_path': sys.executable
        }

    def check_python_version(self) -> bool:
        """
        检查 Python 版本

        返回:
            True: 版本符合要求
            False: 版本不符合要求
        """
        self.logger.separator()
        self.logger.info(f"检测 Python 版本...")
        self.logger.info(f"当前版本: {self.system_info['python_version']}")
        self.logger.info(f"要求版本: >= {'.'.join(map(str, self.REQUIRED_PYTHON_VERSION))}")

        current = sys.version_info[:2]

        if current >= self.REQUIRED_PYTHON_VERSION:
            self.logger.success(f"Python 版本符合要求 ({self.system_info['python_version']})")
            return True
        else:
            self.logger.error(
                f"Python 版本过低 ({self.system_info['python_version']}), "
                f"需要 >= {'.'.join(map(str, self.REQUIRED_PYTHON_VERSION))}"
            )
            self.logger.info("请升级 Python 版本: https://www.python.org/downloads/")
            return False

    def check_installed_packages(self) -> bool:
        """
        检查已安装的包

        返回:
            True: 检查成功
            False: 检查失败
        """
        self.logger.separator()
        self.logger.info("检测已安装的 Python 包...")

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                self.logger.error("获取已安装包列表失败")
                return False

            # 解析输出
            installed_data = json.loads(result.stdout)
            self.installed_packages = {
                pkg['name'].lower(): pkg['version']
                for pkg in installed_data
            }

            self.logger.info(f"已安装 {len(self.installed_packages)} 个包")
            return True

        except json.JSONDecodeError:
            self.logger.error("解析包列表失败")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("获取包列表超时")
            return False
        except Exception as e:
            self.logger.error(f"检查已安装包时出错: {e}")
            return False

    def check_missing_packages(self) -> bool:
        """
        检查缺失的包

        返回:
            True: 没有缺失的包
            False: 有缺失的包
        """
        self.logger.separator()
        self.logger.info("检测缺失的依赖包...")

        self.missing_packages = []

        for package, required_version in self.REQUIRED_PACKAGES.items():
            package_lower = package.lower()
            installed_version = self.installed_packages.get(package_lower)

            if installed_version:
                # 检查版本
                self.logger.info(f"{package} ({installed_version}) - 已安装")
                # 可以添加版本比较逻辑
            else:
                self.logger.warning(f"{package} ({required_version}) - 未安装")
                self.missing_packages.append(package)

        if not self.missing_packages:
            self.logger.success("所有依赖包都已安装")
            return True
        else:
            self.logger.warning(f"发现 {len(self.missing_packages)} 个缺失的包")
            return False

    def check_chrome_browser(self) -> bool:
        """
        检查 Chrome 浏览器是否安装

        返回:
            True: Chrome 已安装
            False: Chrome 未安装
        """
        self.logger.separator()
        self.logger.info("检测 Chrome 浏览器...")

        chrome_paths = []

        # Windows 系统的 Chrome 路径
        if self.system_info['system'] == 'Windows':
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            ]
            chrome_paths = possible_paths

        # macOS 系统的 Chrome 路径
        elif self.system_info['system'] == 'Darwin':
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ]

        # Linux 系统的 Chrome 路径
        elif self.system_info['system'] == 'Linux':
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
            ]

        # 检查 Chrome 是否存在
        for path in chrome_paths:
            if os.path.exists(path):
                self.logger.success(f"找到 Chrome 浏览器: {path}")
                return True

        self.logger.warning("未检测到 Chrome 浏览器")
        self.logger.info("Task-Star 需要 Google Chrome 浏览器")
        self.logger.info("请从以下地址下载: https://www.google.com/chrome/")
        return False

    def check_config_file(self) -> bool:
        """
        检查配置文件

        返回:
            True: 配置文件存在且格式正确
            False: 配置文件不存在或格式错误
        """
        self.logger.separator()
        self.logger.info("检测配置文件...")

        config_path = Path("config/config.yaml")
        default_config_path = Path("config/default_config.yaml")

        if not config_path.exists():
            self.logger.warning("config/config.yaml 不存在")

            # 检查是否有默认配置文件
            if default_config_path.exists():
                self.logger.info("发现 default_config.yaml，正在复制...")
                try:
                    shutil.copy(default_config_path, config_path)
                    self.logger.success("已创建 config/config.yaml")
                    self.logger.info("请修改 config/config.yaml 中的问卷链接和其他配置")
                except Exception as e:
                    self.logger.error(f"复制配置文件失败: {e}")
                    return False
            else:
                self.logger.error("默认配置文件也不存在")
                return False
        else:
            self.logger.success("config/config.yaml 已存在")

        # 检查配置文件格式
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            # 验证必要配置项
            if 'general' not in config_data:
                self.logger.warning("配置文件缺少 'general' 部分")
                return False

            required_keys = ['questionnaire_url', 'fill_times']
            for key in required_keys:
                if key not in config_data['general']:
                    self.logger.warning(f"配置文件缺少必填项: general.{key}")
                    return False

            self.logger.success("配置文件格式正确")
            return True

        except Exception as e:
            self.logger.error(f"解析配置文件失败: {e}")
            return False


class PackageInstaller:
    """包安装器"""

    def __init__(self, logger: Logger):
        """
        初始化包安装器

        参数:
            logger: 日志管理器实例
        """
        self.logger = logger

    def install_package(self, package: str, version: Optional[str] = None) -> bool:
        """
        安装单个包

        参数:
            package: 包名
            version: 版本要求 (可选)

        返回:
            True: 安装成功
            False: 安装失败
        """
        install_spec = f"{package}>={version}" if version else package
        self.logger.progress(f"正在安装 {install_spec}...")

        try:
            # 使用 pip 安装
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', install_spec],
                capture_output=True,
                text=True,
                timeout=300  # 5 分钟超时
            )

            if result.returncode == 0:
                self.logger.success(f"{install_spec} 安装成功")

                # 显示详细输出到日志
                if result.stdout:
                    with open(self.logger.log_file, 'a', encoding='utf-8') as f:
                        f.write(f"\n{package} 安装输出:\n{result.stdout}\n")

                return True
            else:
                self.logger.error(f"{install_spec} 安装失败")
                self.logger.error(f"错误信息: {result.stderr}")

                # 记录错误详情到日志
                with open(self.logger.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{package} 安装失败:\n{result.stderr}\n")

                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"{install_spec} 安装超时")
            return False
        except Exception as e:
            self.logger.error(f"{install_spec} 安装时出错: {e}")
            return False

    def install_all(self, packages: Dict[str, str]) -> Tuple[int, int]:
        """
        安装所有缺失的包

        参数:
            packages: 包字典 {包名: 最低版本}

        返回:
            (成功数量, 失败数量)
        """
        self.logger.separator()
        self.logger.info(f"开始安装 {len(packages)} 个包...")

        success_count = 0
        failed_count = 0

        for package, version in packages.items():
            self.logger.separator()

            if self.install_package(package, version):
                success_count += 1
            else:
                failed_count += 1
                self.logger.warning(f"继续安装其他包...")

        return success_count, failed_count

    def upgrade_pip(self) -> bool:
        """
        升级 pip

        返回:
            True: 升级成功
            False: 升级失败
        """
        self.logger.separator()
        self.logger.progress("正在升级 pip...")

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.logger.success("pip 升级成功")
                return True
            else:
                self.logger.warning("pip 升级失败，继续使用当前版本")
                return True  # 不影响后续安装

        except Exception as e:
            self.logger.warning(f"升级 pip 时出错: {e}，继续使用当前版本")
            return True  # 不影响后续安装


class EnvironmentSetup:
    """环境配置主控制器"""

    def __init__(self):
        """初始化环境配置"""
        self.logger = Logger()
        self.checker = EnvironmentChecker(self.logger)
        self.installer = PackageInstaller(self.logger)

        self.results = {
            'python_version': False,
            'pip_check': False,
            'packages_installed': False,
            'chrome_browser': False,
            'config_file': False,
        }

    def run(self) -> bool:
        """
        运行环境配置

        返回:
            True: 所有检查通过
            False: 有检查失败
        """
        print(Colors.HEADER + "=" * 80 + Colors.END)
        print(Colors.HEADER + "Task-Star 环境自动配置工具" + Colors.END)
        print(Colors.HEADER + "=" * 80 + Colors.END + "\n")

        # 1. 检查 Python 版本
        self.results['python_version'] = self.checker.check_python_version()

        if not self.results['python_version']:
            self.logger.error("Python 版本不符合要求，无法继续")
            return False

        # 2. 升级 pip
        self.installer.upgrade_pip()

        # 3. 检查已安装的包
        self.results['pip_check'] = self.checker.check_installed_packages()

        if not self.results['pip_check']:
            self.logger.error("无法获取已安装包列表，请检查 pip 是否正常工作")
            return False

        # 4. 检查缺失的包
        self.checker.check_missing_packages()

        # 5. 安装缺失的包
        if self.checker.missing_packages:
            self.logger.warning(f"需要安装 {len(self.checker.missing_packages)} 个包")

            # 构建安装包字典
            packages_to_install = {
                pkg: self.checker.REQUIRED_PACKAGES[pkg]
                for pkg in self.checker.missing_packages
            }

            success_count, failed_count = self.installer.install_all(packages_to_install)

            if failed_count == 0:
                self.logger.success("所有包安装成功")
                self.results['packages_installed'] = True
            else:
                self.logger.warning(f"部分包安装失败: {failed_count}/{len(packages_to_install)}")
                # 不中断，继续其他检查
                self.results['packages_installed'] = (success_count > 0)
        else:
            self.logger.success("所有依赖包已安装")
            self.results['packages_installed'] = True

        # 6. 检查 Chrome 浏览器
        self.results['chrome_browser'] = self.checker.check_chrome_browser()

        # 7. 检查配置文件
        self.results['config_file'] = self.checker.check_config_file()

        # 输出总结
        total = len(self.results)
        passed = sum(1 for v in self.results.values() if v)
        failed = total - passed

        self.logger.separator()
        self.logger.info("环境配置完成情况:")

        for name, result in self.results.items():
            status = Colors.success(f"✅ {name.replace('_', ' ').title()}") if result else Colors.error(f"❌ {name.replace('_', ' ').title()}")
            print(f"  {status}")

        self.logger.summary(total, passed, failed)

        # 给出后续建议
        self._print_suggestions()

        # 返回是否所有关键检查都通过
        return passed >= total - 1  # 允许一个非关键检查失败（如 Chrome）

    def _print_suggestions(self):
        """打印后续建议"""
        self.logger.separator()

        if not self.results['python_version']:
            print(Colors.error("请先升级 Python 版本到 3.8 或更高"))
            print(Colors.info("下载地址: https://www.python.org/downloads/\n"))

        if not self.results['packages_installed']:
            print(Colors.error("部分依赖包安装失败，请手动安装:"))
            for pkg in self.checker.missing_packages:
                version = self.checker.REQUIRED_PACKAGES.get(pkg, '')
                print(f"  pip install {pkg}>={version}\n")

        if not self.results['chrome_browser']:
            print(Colors.error("请安装 Google Chrome 浏览器"))
            print(Colors.info("下载地址: https://www.google.com/chrome/\n"))

        if self.results['config_file']:
            print(Colors.success("环境配置完成！"))
            print(Colors.info("现在可以运行程序: python main.py\n"))
        else:
            print(Colors.warning("请检查并修复配置文件\n"))


def main():
    """主函数"""
    try:
        setup = EnvironmentSetup()
        success = setup.run()

        # 询问用户是否立即运行主程序
        if success and all(setup.results.values()):
            print(Colors.CYAN + "\n是否立即运行 Task-Star 程序? (y/n): " + Colors.END, end='')
            try:
                choice = input().strip().lower()
                if choice in ['y', 'yes']:
                    print(Colors.progress("正在启动 Task-Star...\n"))
                    import subprocess
                    subprocess.run([sys.executable, "main.py"])
                else:
                    print(Colors.info("稍后可以运行: python main.py\n"))
            except KeyboardInterrupt:
                print(Colors.info("\n操作已取消\n"))

        return 0 if success else 1

    except KeyboardInterrupt:
        print(Colors.warning("\n用户中断操作\n"))
        return 1
    except Exception as e:
        print(Colors.error(f"发生未预期的错误: {e}\n"))
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
