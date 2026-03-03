import yaml
import os
from pathlib import Path
from typing import Dict, List, Any


class ConfigLoader:
    """
    配置文件加载器

    功能说明:
        负责加载、验证和管理 YAML 配置文件
        提供配置项访问的便捷接口
    """

    def __init__(self, config_path: str = None):
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
        # 1. 确定配置文件路径
        if config_path is None:
            # 如果未指定路径，使用默认路径
            # 项目根目录/config/config.yaml
            root_dir = Path(__file__).parent.parent.parent  # 回退三级目录到项目根目录
            config_path = root_dir / "config" / "config.yaml"

        # 转换为 Path 对象，便于路径操作
        self.config_path = Path(config_path)

        # 2. 加载配置文件
        self.config = self._load_config()

        # 3. 验证配置文件的完整性
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
        # 检查配置文件是否存在
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"配置文件未找到: {self.config_path}\n"
                f"请按以下步骤操作:\n"
                f"1. 复制 config/default_config.yaml 文件\n"
                f"2. 重命名为 config.yaml\n"
                f"3. 根据实际情况修改配置内容"
            )

        # 读取并解析 YAML 文件
        # 使用 utf-8 编码以支持中文注释和内容
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _validate_config(self):
        """
        验证配置文件的必要字段

        检查内容:
            1. 是否存在 'general' 部分
            2. 是否存在必填的通用配置项
               - questionnaire_url: 问卷链接
               - fill_times: 填写次数

        抛出异常:
            ValueError: 配置项缺失或无效
        """
        # 检查 general 部分
        if 'general' not in self.config:
            raise ValueError(
                "配置文件缺少 'general' 部分\n"
                "请在配置文件中添加:\n"
                "general:\n"
                "  questionnaire_url: \"你的问卷链接\"\n"
                "  fill_times: 10"
            )

        # 检查必填项
        required_general_keys = ['questionnaire_url', 'fill_times']
        for key in required_general_keys:
            if key not in self.config['general']:
                raise ValueError(
                    f"配置项 general.{key} 是必填项\n"
                    "请在配置文件的 general 部分添加该项"
                )

        # 可选: 验证问卷链接格式（简单验证）
        url = self.config['general'].get('questionnaire_url', '')
        if not url or not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError(
                f"问卷链接格式不正确: {url}\n"
                "请确保链接以 http:// 或 https:// 开头"
            )

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

    @classmethod
    def reload(cls):
        """
        重新加载全局配置

        使用场景:
            - 修改了配置文件后，需要在不重启程序的情况下重新加载
            - 通过 UI 界面修改配置后，立即生效

        注意事项:
            - 此方法会重新读取 config.yaml 文件
            - 重新加载时会进行完整的验证
            - 如果重新加载失败，会保留之前的配置
        """
        global config  # 引用全局配置对象
        try:
            # 创建新的配置加载器实例
            new_config = ConfigLoader()
            # 更新全局配置
            config = new_config
            print("配置重新加载成功")
        except Exception as e:
            print(f"配置重新加载失败: {e}")


# 创建全局配置对象，方便其他模块导入使用
# 其他模块可以通过 from task_star.config import config 来访问配置
config = None  # 类型: Optional[ConfigLoader]

try:
    # 尝试加载配置
    config = ConfigLoader()
except Exception as e:
    # 如果加载失败，输出错误信息并将 config 设为 None
    print(f"配置加载失败: {e}")
    print("提示: 请检查 config/config.yaml 文件是否存在且格式正确")
    config = None
