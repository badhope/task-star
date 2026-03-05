import yaml
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from .utils import logger
from .exceptions import ConfigError


class ConfigLoader:
    """
    配置文件加载器

    功能说明:
        负责加载、验证和管理 YAML 配置文件
        提供配置项访问的便捷接口
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器

        参数说明:
            config_path: 配置文件的完整路径
                       如果为 None，则使用默认路径: 项目根目录/config/config.yaml

        默认路径说明:
            项目根目录是包含 pyproject.toml 的目录
            配置文件位于: <项目根目录>/config/config.yaml

        异常处理:
            - 如果配置文件不存在，抛出 FileNotFoundError
            - 如果配置格式错误，抛出 yaml.YAMLError
            - 如果缺少必填项，抛出 ValueError
        """
        if config_path is None:
            root_dir = Path(__file__).parent.parent.parent
            config_path = root_dir / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self._raw_config = {}
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        加载 YAML 配置文件

        返回值:
            Dict[str, Any]: 解析后的配置字典

        抛出异常:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML 格式错误
        """
        if not self.config_path.exists():
            raise ConfigError(
                f"配置文件未找到: {self.config_path}\n"
                f"请按以下步骤操作:\n"
                f"1. 复制 config/default_config.yaml 文件\n"
                f"2. 重命名为 config.yaml\n"
                f"3. 根据实际情况修改配置内容"
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._raw_config = yaml.safe_load(f) or {}
                return self._raw_config
        except yaml.YAMLError as e:
            raise ConfigError(f"配置文件格式错误: {e}")

    def _validate_config(self):
        """
        验证配置文件的必要字段

        检查内容:
            1. 是否存在 'general' 部分
            2. 是否存在必填的通用配置项
               - questionnaire_url: 问卷链接
               - fill_times: 填写次数

        抛出异常:
            ConfigError: 配置项缺失或无效
        """
        if 'general' not in self.config:
            raise ConfigError(
                "配置文件缺少 'general' 部分\n"
                "请在配置文件中添加:\n"
                "general:\n"
                "  questionnaire_url: \"你的问卷链接\"\n"
                "  fill_times: 10"
            )

        required_general_keys = ['questionnaire_url', 'fill_times']
        for key in required_general_keys:
            if key not in self.config['general']:
                raise ConfigError(
                    f"配置项 general.{key} 是必填项\n"
                    "请在配置文件的 general 部分添加该项"
                )

        url = self.config['general'].get('questionnaire_url', '')
        if not url or not (url.startswith('http://') or url.startswith('https://')):
            raise ConfigError(
                f"问卷链接格式不正确: {url}\n"
                "请确保链接以 http:// 或 https:// 开头"
            )

        fill_times = self.config['general'].get('fill_times', 0)
        if not isinstance(fill_times, int) or fill_times < 1:
            raise ConfigError(
                f"填写次数必须为正整数，当前值: {fill_times}"
            )

        interval = self.config['general'].get('interval_seconds', 3)
        if not isinstance(interval, (int, float)) or interval < 0:
            raise ConfigError(
                f"提交间隔必须为非负数，当前值: {interval}"
            )

        strategy = self.config.get('strategy', {})
        if 'multi_choice' in strategy:
            mc = strategy['multi_choice']
            min_sel = mc.get('min_select', 2)
            max_sel = mc.get('max_select', 3)
            if min_sel > max_sel and max_sel != -1:
                raise ConfigError(
                    f"多选题配置错误: min_select({min_sel}) 不能大于 max_select({max_sel})"
                )

        logger.info("配置文件验证通过")

    @property
    def general(self) -> Dict[str, Any]:
        """
        获取通用配置

        返回值:
            包含以下键的字典:
                - questionnaire_url: 问卷链接 (str)
                - fill_times: 填写次数 (int)
                - interval_seconds: 提交间隔 (int)
                - headless: 是否后台运行 (bool)
                - auto_submit: 是否自动提交 (bool)
        """
        return self.config.get('general', {})

    @property
    def strategy(self) -> Dict[str, Any]:
        """
        获取策略配置

        返回值:
            包含以下键的字典:
                - single_choice: 单选题策略 (str)
                - multi_choice: 多选题策略 (dict)
                - fill_blanks: 填空题答案池 (dict)
        """
        return self.config.get('strategy', {})

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        参数:
            key: 配置键，支持点号分隔的嵌套键，如 'general.fill_times'
            default: 默认值

        返回:
            配置值或默认值
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """
        设置配置项

        参数:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self, path: Optional[str] = None):
        """
        保存配置到文件

        参数:
            path: 保存路径，默认为当前配置文件路径
        """
        save_path = Path(path) if path else self.config_path
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            logger.info(f"配置已保存到: {save_path}")
        except Exception as e:
            raise ConfigError(f"保存配置失败: {e}")

    def reload(self):
        """
        重新加载配置文件
        """
        self.config = self._load_config()
        self._validate_config()
        logger.info("配置重新加载成功")

    @classmethod
    def create_default(cls, path: str) -> 'ConfigLoader':
        """
        创建默认配置文件

        参数:
            path: 配置文件路径

        返回:
            ConfigLoader 实例
        """
        default_config = {
            'general': {
                'questionnaire_url': 'https://www.wjx.cn/jq/12345678.aspx',
                'fill_times': 5,
                'auto_submit': True,
                'interval_seconds': 5,
                'headless': False,
                'retry_count': 3,
                'page_timeout': 30
            },
            'strategy': {
                'single_choice': 'random',
                'multi_choice': {
                    'min_select': 2,
                    'max_select': 3
                },
                'fill_blanks': {
                    1: ['张三', '李四', '王五'],
                    2: ['计算机科学与技术', '软件工程', '人工智能']
                }
            }
        }
        
        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
        logger.info(f"默认配置文件已创建: {path}")
        return cls(path)

    def __repr__(self) -> str:
        return f"ConfigLoader(path={self.config_path})"


def reload_global_config() -> Optional[ConfigLoader]:
    """
    重新加载全局配置

    返回值:
        新的配置对象，如果加载失败返回 None
    """
    global config
    try:
        new_config = ConfigLoader()
        config = new_config
        logger.info("全局配置重新加载成功")
        return new_config
    except Exception as e:
        logger.error(f"全局配置重新加载失败: {e}")
        return None


config: Optional[ConfigLoader] = None

try:
    config = ConfigLoader()
except ConfigError as e:
    logger.error(f"配置加载失败: {e}")
    logger.warning("请检查 config/config.yaml 文件是否存在且格式正确")
    config = None
except Exception as e:
    logger.error(f"配置加载时发生未知错误: {e}")
    config = None
