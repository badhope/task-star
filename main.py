"""
Task-Star 问卷自动填写助手 - 主入口模块

功能说明:
    这是程序的主入口文件，负责启动 GUI 应用程序。

启动流程:
    1. 添加 src 目录到 Python 路径，确保模块可以正确导入
    2. 导入 TaskStarApp 类（GUI 主窗口）
    3. 创建应用实例并启动主循环

异常处理:
    捕获启动过程中的异常，输出详细错误信息，
    等待用户确认后再退出，方便查看错误信息。
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
# 这样才能正确导入 task_star 包中的模块
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 导入 GUI 应用类
from ui_app import TaskStarApp

# 程序入口点
if __name__ == "__main__":
    try:
        # 创建并启动 GUI 应用
        app = TaskStarApp()
        # 进入主事件循环，保持窗口显示
        app.mainloop()
    except Exception as e:
        # 捕获启动过程中的异常
        print(f"启动失败：{e}")
        # 输出详细的错误堆栈信息，便于调试
        import traceback
        traceback.print_exc()
        # 等待用户按回车键，避免窗口立即关闭导致看不到错误信息
        input("按回车键退出...")
