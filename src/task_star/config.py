"""配置管理"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .utils import logger
from .exceptions import ConfigError


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            root_dir = Path(__file__).parent.parent.parent
            config_path = root_dir / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise ConfigError(
                f"配置文件未找到：{self.config_path}\n"
                f"请复制 config/default_config.yaml 为 config.yaml 并修改配置"
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"配置文件格式错误：{e}")

    def _validate_config(self):
        """验证配置"""
        if 'general' not in self.config:
            raise ConfigError("配置文件缺少 'general' 部分")

        required_keys = ['questionnaire_url', 'fill_times']
        for key in required_keys:
            if key not in self.config['general']:
                raise ConfigError(f"配置项 general.{key} 是必填项")

        url = self.config['general'].get('questionnaire_url', '')
        if not url or not (url.startswith('http://') or url.startswith('https://')):
            raise ConfigError(f"问卷链接格式不正确：{url}")

        fill_times = self.config['general'].get('fill_times', 0)
        if not isinstance(fill_times, (int, float)) or fill_times < 1:
            raise ConfigError(f"填写次数必须为正整数，当前值：{fill_times}")
        
        interval = self.config['general'].get('interval_seconds', 3)
        if not isinstance(interval, (int, float)) or interval < 0:
            raise ConfigError(f"提交间隔必须为非负数，当前值：{interval}")
        
        retry_count = self.config['general'].get('retry_count', 3)
        if not isinstance(retry_count, int) or retry_count < 0:
            raise ConfigError(f"重试次数必须为非负整数，当前值：{retry_count}")

        strategy = self.config.get('strategy', {})
        if strategy:
            mc = strategy.get('multi_choice', {})
            if mc:
                min_sel = mc.get('min_select', 2)
                max_sel = mc.get('max_select', 3)
                if min_sel < 1 or (max_sel != -1 and max_sel < 1):
                    raise ConfigError(f"多选题选择数配置错误：min_select={min_sel}, max_select={max_sel}")
                if max_sel != -1 and min_sel > max_sel:
                    raise ConfigError(f"多选题配置错误：min_select({min_sel}) 不能大于 max_select({max_sel})")

        logger.info("配置文件验证通过")

    @property
    def general(self) -> Dict[str, Any]:
        """获取通用配置"""
        return self.config.get('general', {})

    @property
    def strategy(self) -> Dict[str, Any]:
        """获取策略配置"""
        return self.config.get('strategy', {})

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


config: Optional[ConfigLoader] = None

try:
    config = ConfigLoader()
except ConfigError as e:
    logger.error(f"配置加载失败：{e}")
    logger.warning("请检查 config/config.yaml 文件是否存在且格式正确")
    config = None
except Exception as e:
    logger.error(f"配置加载失败：{e}")
    config = None


def reload_global_config() -> Optional[ConfigLoader]:
    """重新加载全局配置"""
    global config
    try:
        new_config = ConfigLoader()
        config = new_config
        logger.info("全局配置重新加载成功")
        return new_config
    except Exception as e:
        logger.error(f"全局配置重新加载失败：{e}")
        return None
