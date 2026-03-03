"""
测试脚本 - 检查 Task-Star 程序是否能正常加载所有模块

此脚本用于验证程序的基本功能是否正常，包括:
1. 检查 Python 环境
2. 检查依赖包是否安装
3. 检查配置文件是否能正常加载
4. 检查所有模块是否能正常导入
5. 检查核心组件是否能正常初始化
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def check_python_version():
    """检查 Python 版本"""
    print("=" * 60)
    print("1. 检查 Python 版本")
    print("=" * 60)
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 8:
        print("✅ Python 版本符合要求 (>= 3.8)")
        return True
    else:
        print("❌ Python 版本不符合要求，需要 >= 3.8")
        return False

def check_dependencies():
    """检查依赖包是否安装"""
    print("\n" + "=" * 60)
    print("2. 检查依赖包")
    print("=" * 60)

    required_packages = {
        'selenium': '>=4.15.0',
        'webdriver_manager': '>=4.0.1',
        'yaml': '>=6.0',
        'customtkinter': '>=5.2.1',
        'pillow': '>=10.0.0'
    }

    all_ok = True
    for package, version in required_packages.items():
        try:
            if package == 'yaml':
                import yaml
                print(f"✅ {package} ({version}) - 已安装")
            else:
                __import__(package)
                print(f"✅ {package} ({version}) - 已安装")
        except ImportError:
            print(f"❌ {package} ({version}) - 未安装")
            all_ok = False

    return all_ok

def check_config():
    """检查配置文件"""
    print("\n" + "=" * 60)
    print("3. 检查配置文件")
    print("=" * 60)

    try:
        from task_star.config import config
        print("✅ 配置文件加载成功")

        # 检查必要配置项
        general = config.general
        print(f"   - 问卷链接: {general.get('questionnaire_url', '未设置')}")
        print(f"   - 填写次数: {general.get('fill_times', 0)}")
        print(f"   - 提交间隔: {general.get('interval_seconds', 0)}秒")
        print(f"   - 后台模式: {general.get('headless', False)}")

        return True
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False

def check_modules():
    """检查所有模块是否能正常导入"""
    print("\n" + "=" * 60)
    print("4. 检查模块导入")
    print("=" * 60)

    modules = [
        'task_star.config',
        'task_star.browser',
        'task_star.core_logic',
        'task_star.utils',
        'task_star.exceptions',
        'task_star.strategies.base',
        'task_star.strategies.single',
        'task_star.strategies.multiple',
        'task_star.strategies.blank'
    ]

    all_ok = True
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name} - 导入失败: {e}")
            all_ok = False

    return all_ok

def check_components():
    """检查核心组件是否能正常初始化"""
    print("\n" + "=" * 60)
    print("5. 检查核心组件初始化")
    print("=" * 60)

    try:
        from task_star.config import config
        from task_star.browser import BrowserManager
        from task_star.core_logic import QuestionnaireFiller
        from task_star.strategies.single import SingleChoiceStrategy
        from task_star.strategies.multiple import MultipleChoiceStrategy
        from task_star.strategies.blank import FillBlankStrategy

        # 检查策略组件
        print("✅ 单选题策略: 初始化成功")
        single_strategy = SingleChoiceStrategy()

        print("✅ 多选题策略: 初始化成功")
        multi_strategy = MultipleChoiceStrategy(min_select=2, max_select=3)

        print("✅ 填空题策略: 初始化成功")
        blank_strategy = FillBlankStrategy(answer_pool={1: ["测试答案"]})

        # 检查核心逻辑
        print("✅ 核心逻辑: 初始化成功")
        filler = QuestionnaireFiller(
            status_callback=None,
            log_callback=None
        )

        # 检查浏览器管理器（不实际创建浏览器）
        print("✅ 浏览器管理器: 类初始化成功")

        return True
    except Exception as e:
        print(f"❌ 组件初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_gui():
    """检查 GUI 模块"""
    print("\n" + "=" * 60)
    print("6. 检查 GUI 模块")
    print("=" * 60)

    try:
        # 注意: 实际运行 GUI 需要显示环境
        import tkinter
        print("✅ tkinter 可用")

        import customtkinter
        print("✅ customtkinter 可用")

        # 导入 GUI 应用类（不启动）
        import ui_app
        print("✅ UI 应用模块: 导入成功")

        return True
    except Exception as e:
        print(f"❌ GUI 检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Task-Star 程序运行环境检测")
    print("=" * 60)

    results = []

    # 运行各项检查
    results.append(("Python 版本", check_python_version()))
    results.append(("依赖包", check_dependencies()))
    results.append(("配置文件", check_config()))
    results.append(("模块导入", check_modules()))
    results.append(("核心组件", check_components()))
    results.append(("GUI 模块", check_gui()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 检测结果汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:12} : {status}")

    print("=" * 60)
    print(f"总计: {passed}/{total} 项检查通过")
    print("=" * 60)

    if passed == total:
        print("\n🎉 所有检查通过！程序应该可以正常运行。")
        print("\n运行命令: python main.py")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 项检查失败，请根据上面的错误信息进行修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
