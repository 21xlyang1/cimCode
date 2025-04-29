import threading
import time
from videoCaptureModule import VideoCaptureModule
from config import RTSP_URL, RESTART_INTERVAL
from utils import setup_logger

logger = setup_logger(__name__)


class ObjectPoolManager(threading.Thread):
    def __init__(self, frame_queue):
        """
        初始化对象池管理器。

        参数:
        frame_queue (Queue): 存放视频帧的队列。
        """
        super().__init__()
        self.frame_queue = frame_queue
        self.running = True
        # 创建三个视频捕获模块
        # 创建一个空列表来存放 VideoCaptureModule 实例
        self.capture_modules = []

        # 使用一个循环来创建三个 VideoCaptureModule 实例，并将它们添加到列表中
        for _ in range(3):
            module = VideoCaptureModule(RTSP_URL, frame_queue)
            self.capture_modules.append(module)

    def run(self):
        """
        运行对象池管理器，启动所有的视频捕获模块并定期重启它们。
        """
        for module in self.capture_modules:
            module.start()

        while self.running:
            time.sleep(RESTART_INTERVAL)
            self.restart_modules()

    def stop(self):
        """
        停止对象池管理器和所有的视频捕获模块。
        """
        self.running = False
        for module in self.capture_modules:
            module.stop()
        for module in self.capture_modules:
            module.join()

    def restart_modules(self):
        """
        重启所有已经停止运行的视频捕获模块。
        """
        for module in self.capture_modules:
            if not module.is_alive():
                logger.info(f"Restarting {module}")
                new_module = VideoCaptureModule(RTSP_URL, self.frame_queue)
                self.capture_modules.remove(module)
                self.capture_modules.append(new_module)
                new_module.start()
