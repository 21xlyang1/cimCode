import threading
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
                    logger.warning(f"Module {module} heartbeat missed. Restarting...")
                    self.restart_module(module)
            time.sleep(self.interval)

    def stop(self):
        """
        停止心跳监测器。
        """
        self.running = False

    def restart_module(self, module):
        """
        重启指定的模块。
        """
        module.stop()
        new_module = module.__class__(module.rtsp_url, module.frame_queue)  # 假设模块有相同的构造函数
        self.modules.remove(module)
        self.modules.append(new_module)
        new_module.start()
