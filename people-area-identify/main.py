import cv2
import numpy as np

# 全局变量，用于存储多边形顶点
vertices = []
drawing = False  # 初始化为False，表示不在绘制中

# 鼠标事件
def OnMouseAction(event, x, y, flags, param):
    global vertices, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        if not drawing:
            # 鼠标左键按下，开始绘制多边形
            vertices = [(x, y)]
            drawing = True
        else:
            # 如果已经在绘制中，重置顶点列表
            vertices = [(x, y)]
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        # 鼠标左键按下并移动，增加多边形顶点
        vertices.append((x, y))
    elif event == cv2.EVENT_LBUTTONUP:
        # 鼠标左键释放，完成多边形绘制
        vertices.append(vertices[-1])  # 闭合多边形
        drawing = False

# 导出多边形顶点到文件
def exportVertices(filename, vertices):
    with open(filename, 'w') as file:
        for vertex in vertices:
            file.write(f"{vertex[0]} {vertex[1]}\n")

# 从文件加载多边形顶点
def loadVertices(filename):
    vertices = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                x, y = map(int, line.strip().split())
                vertices.append((x, y))
    except FileNotFoundError:
        print(f"No vertices file found: {filename}")
    return vertices

# 主程序
if __name__ == '__main__':
    # 加载Haar级联分类器模型
    cascade_classifier = cv2.CascadeClassifier('weights/haarcascade_fullbody.xml')

    # 加载视频
    video_capture = cv2.VideoCapture('./data/test.mp4')
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', OnMouseAction)

    # 尝试从文件加载顶点
    vertices = loadVertices('roidata/vertices.txt')

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bodies = cascade_classifier.detectMultiScale(gray, 1.1, 4)

        if vertices:
            cv2.polylines(frame, [np.array(vertices, dtype=np.int32)], True, (0, 0, 255), 2)
            for (x, y, w, h) in bodies:
                bottom_center_x = int(x + w // 2)
                bottom_center_y = int(y + h)
                cv2.circle(frame, (bottom_center_x, bottom_center_y), 2, (0, 0, 255), -1)
                if cv2.pointPolygonTest(np.array(vertices, dtype=np.int32), (bottom_center_x, bottom_center_y), False) > 0:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        cv2.imshow('image', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e'):
            if vertices:
                exportVertices('roidata/vertices.txt', vertices)
                print("Vertices have been exported.")

    video_capture.release()
    cv2.destroyAllWindows()
