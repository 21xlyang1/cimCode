import logging
import os
from datetime import datetime


def setup_logger(name, log_dir=None, level=logging.INFO):
    """
    设置日志记录器。

    参数:
    name (str): 日志记录器的名称。
    log_dir (str): 日志文件存储的目录。默认为项目根目录下的 /logManager/logs。
    level (int): 日志记录级别。

    返回:
    logger (Logger): 配置好的日志记录器。
    """
    if log_dir is None:
        # 设置默认日志目录为项目根目录下的 /logManager/logs
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

    logger = logging.getLogger(name)

    # 防止重复添加处理器
    if not logger.hasHandlers():
        logger.setLevel(level)

        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 获取当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(log_dir, current_date)

        # 创建日期目录
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)

        # 创建日志文件路径
        log_file = os.path.join(date_dir, f"{name}.log")

        # 创建文件处理器，设置编码为 UTF-8
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)

        # 创建日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 添加处理器到日志记录器
        logger.addHandler(file_handler)

    return logger


# 配置各类日志记录器
mainLogger = setup_logger("main")
videoCaptureLogger = setup_logger("videoCapture")
heartbeatMonitorLogger = setup_logger("heartbeatMonitor")
taskQueueLogger = setup_logger("taskQueue")