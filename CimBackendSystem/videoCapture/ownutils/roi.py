import cv2

class ROI:
    def __init__(self):
        self.vertices = []
        self.drawing = False  # 初始化为False，表示不在绘制中
        self.flag = False
        self.name = None

    # 绘制ROI区域
    def draw_roi(self, event, x, y, flags, param):
        # 按下鼠标左键触发绘制roi区域
        if event == cv2.EVENT_LBUTTONDOWN:
            if not self.drawing:
                self.vertices = [(x, y)]
                self.drawing = True
            else:
                self.vertices = [(x, y)]  # 如果已经在绘制中，重置顶点列表
        # 移动鼠标添加新的位置
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.vertices.append((x, y))
        # 释放鼠标左键，完成roi区域的绘制
        elif event == cv2.EVENT_LBUTTONUP:
            self.vertices.append(self.vertices[-1])  # 确保绘制的是闭合的多边形
            self.drawing = False
            self.flag = True


    # 导出绘制好的ROI区域
    def export_vertices(self, filename):
        path = "./roidata/" + str(filename)
        try:
            with open(path, 'w') as file:
                for vertx in self.vertices:
                    file.write(f"{vertx[0]} {vertx[1]}\n")

            msg = str(filename) + " is exported successfully."
        except Exception as e:
            msg = str(e) + " error occur."
        return msg

    # 加载需要使用的ROI区域
    def load_vertices(self, filename):
        path = "./roidata/" + str(filename)
        try:
            with open(path, 'r') as file:
                for line in file:
                    x, y = map(int, line.strip().split())
                    self.vertices.append((x, y))
            msg = str(filename) + " is loaded successfully."
        except FileNotFoundError:
            msg = "No vertices file found: " + str(filename)
        return msg
