#!/usr/bin/env python3
"""Task-Star 问卷自动填写助手 - CLI 版本"""

import sys
import signal
import argparse
from pathlib import Path

src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from task_star.core_logic import QuestionnaireFiller
from task_star.config import config, reload_global_config
from task_star.utils import logger


class CLIHandler:
    """CLI 处理器"""

    def __init__(self):
        self.filler = None
        self.running = False

    def signal_handler(self, signum, frame):
        """信号处理"""
        logger.info("\n用户中断信号，正在停止...")
        self.running = False
        if self.filler:
            self.filler.stop()

    def run(self, times: int = None, headless: bool = False):
        """运行任务"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        if config is None:
            logger.error("配置加载失败，请检查 config/config.yaml")
            return 1

        try:
            if times:
                logger.info(f"命令行覆盖填写次数：{times}")
                config.config['general']['fill_times'] = times
            
            if headless:
                logger.info(f"命令行覆盖后台模式：{headless}")
                config.config['general']['headless'] = headless

            self.filler = QuestionnaireFiller(
                status_callback=lambda msg: logger.info(f"[状态] {msg}"),
                log_callback=lambda msg: logger.info(msg),
                progress_callback=lambda c, t: logger.info(f"[进度] {c}/{t}")
            )

            self.running = True
            self.filler.run()

            stats = self.filler.statistics
            logger.info(f"\n{'='*60}")
            logger.info(f"任务完成")
            logger.info(f"成功：{stats['success']} 份")
            logger.info(f"失败：{stats['fail']} 份")
            logger.info(f"总计：{stats['total']} 份")
            logger.info(f"{'='*60}")

            return 0 if stats['fail'] == 0 else 1

        except Exception as e:
            logger.error(f"任务执行失败：{e}")
            return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Task-Star 问卷自动填写助手',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                    # 使用配置文件运行
  python main.py -t 20              # 填写 20 次
  python main.py --headless         # 后台运行
  python main.py -t 50 --headless   # 后台填写 50 次
        """
    )

    parser.add_argument(
        '-t', '--times',
        type=int,
        help='填写次数（覆盖配置文件）'
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='后台运行模式（无界面）'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='Task-Star 1.0.0'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Task-Star 问卷自动填写助手 v1.0.0")
    print("=" * 60)
    print()

    handler = CLIHandler()
    return handler.run(times=args.times, headless=args.headless)


if __name__ == "__main__":
    sys.exit(main())
