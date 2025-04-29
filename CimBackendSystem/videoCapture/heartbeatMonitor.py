import threading
import time
from utils import setup_logger

logger = setup_logger(__name__)


class HeartbeatMonitor(threading.Thread):
    def __init__(self, modules, interval):
        """
        初始化心跳监测器。

        参数:
        modules (list): 需要监测的模块列表。
        interval (int): 心跳检测的时间间隔（秒）。
        """
        super().__init__()
        self.modules = modules
        self.interval = interval
        self.running = True

    def run(self):
        """
        运行心跳监测器，定期检查所有模块的心跳信号。
        """
        while self.running:
            for module in self.modules:
                last_heartbeat = module.get_heartbeat()
                if time.time() - last_heartbeat > self.interval:
                    logger.warning(f"Module {module} heartbeat missed.")
            time.sleep(self.interval)

    def stop(self):
        """
        停止心跳监测器。
        """
        self.running = False
