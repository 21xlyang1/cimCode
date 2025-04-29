import cv2

# RTSP流的URL
rtsp_url = 'rtsp://14.22.124.194:10003/3TPBA35144003JD_0?key=7eb33280af3b018a5b07b7ea5f5af37f&tk=e94d2204-ae27-4e6b-9434-d109c24c162a'

# 使用cv2.VideoCapture打开RTSP流
cap = cv2.VideoCapture(rtsp_url)

# 检查流是否成功打开
if not cap.isOpened():
    print("无法打开视频流")
    exit()

# 从RTSP流中读取单个帧
ret, frame = cap.read()

# 检查帧是否正确读取
if not ret:
    print("无法读取帧")
    cap.release()
    exit()

# 保存帧为图片
image_path = './data/test.png'
cv2.imwrite(image_path, frame)

# 释放资源
cap.release()
print(f"图片已保存到 {image_path}")