import json

import cv2
import numpy as np


class ROIDrawer:
    def __init__(self, window_name, image):
        self.window_name = window_name
        self.image = image
        self.drawing = False
        self.rois = []
        self.current_roi = []
        self.colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255)]  # 可以添加更多颜色以区分不同的ROI

    def draw_roi(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if not self.drawing:  # 开始新的ROI绘制
                self.drawing = True
                self.current_roi = [(x, y)]
            else:  # 如果已经在绘制中，闭合当前ROI并开始新的ROI
                self.current_roi.append(self.current_roi[0])  # 闭合多边形
                self.rois.append(self.current_roi)  # 添加到ROI列表
                self.current_roi = [(x, y)]  # 开始新的ROI
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:  # 鼠标移动时添加顶点
            self.current_roi.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP and self.drawing:  # 鼠标左键释放，完成ROI绘制
            self.current_roi.append(self.current_roi[0])  # 闭合多边形
            self.rois.append(self.current_roi)  # 添加到ROI列表
            self.current_roi = []  # 重置当前ROI
            self.drawing = False  # 标记绘制结束

    def draw_all_rois(self):
        for roi in self.rois:
            color = self.colors[len(self.rois) % len(self.colors)]  # 为每个ROI选择不同的颜色
            cv2.polylines(self.image, [np.array(roi, dtype=np.int32)], True, color, 2)  # 确保roi是numpy数组

    def run(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.draw_roi)
        while True:
            cv2.imshow(self.window_name, self.image)
            self.draw_all_rois()

            # 检查退出条件，这里以ESC键为例
            if cv2.waitKey(1) & 0xFF == 27:  # ESC键的ASCII码是27
                break

        return self.rois

    def save_rois_to_json(self, filename):
        roi_dict = {}
        for idx, roi in enumerate(self.rois):
            name = input(f"Enter name for ROI {idx + 1}: ")  # 获取用户输入的ROI名称
            roi_dict[name] = roi

        with open(filename, 'w') as f:
            json.dump(roi_dict, f, indent=4)  # 使用json.dump()保存为JSON格式


# 初始化ROI绘制器
roi_drawer = ROIDrawer('Draw ROI', cv2.imread('./data/test.png'))

# 开始绘制ROI
rois = roi_drawer.run()

# 释放窗口
cv2.destroyAllWindows()

# 保存ROI到JSON文件
roi_drawer.save_rois_to_json('rois.json')
