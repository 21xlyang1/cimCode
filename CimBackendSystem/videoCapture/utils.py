# 工具模块，包含一些辅助函数

import logging


def setup_logger(name, level=logging.INFO):
    """
    设置日志记录器。

    参数:
    name (str): 日志记录器的名称。
    level (int): 日志记录级别。

    返回:
    logger (Logger): 配置好的日志记录器。
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
