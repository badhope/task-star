import logging
from pathlib import Path

# 配置日志系统
# 级别说明:
#   DEBUG: 详细的信息，通常只在诊断问题时使用
#   INFO: 确认程序按预期运行
#   WARNING: 表示发生了意外情况，但程序仍能继续运行
#   ERROR: 由于更严重的问题，程序无法执行某些功能
#   CRITICAL: 严重错误，程序本身可能无法继续运行
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        # 可以在这里添加文件输出: logging.FileHandler('taskstar.log')
    ]
)

# 创建全局logger实例，供所有模块使用
# TaskStar 作为日志名称，方便在日志中识别来源
logger = logging.getLogger('TaskStar')


def setup_logger(level=logging.INFO, log_file=None):
    """
    设置日志级别和输出文件

    参数说明:
        level: 日志级别，默认为 logging.INFO
        log_file: 日志文件路径，如果指定则将日志同时输出到文件

    返回值:
        配置好的logger对象
    """
    logger.setLevel(level)

    # 如果指定了日志文件，添加文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger():
    """
    获取全局logger对象

    返回值:
        全局logger实例
    """
    return logger
