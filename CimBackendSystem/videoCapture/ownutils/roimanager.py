import cv2
import json
import numpy as np


class ROIManager:
    def __init__(self):
        self.roi_dict = {}  # 加载时存储绘制好的roi区域的坐标

    def load_rois_from_json(self, filename):
        with open(filename, 'r') as f:
            self.roi_dict = json.load(f)

    def draw_rois(self, frame):
        cut=1
        for name, vertices in self.roi_dict.items():
            # 将ROI顶点转换为numpy数组，并指定点的类型为整数
            roi_vertices = np.array(vertices, dtype=np.int32)
            color=[(0,0,255),(32,165,218),(0,255,255)]
            # 使用cv2.polylines绘制闭合的多边形ROI区域
            cv2.polylines(frame, [roi_vertices], True, color[cut-1], 2)  # 绿色线条
            cut+=1
        return frame


