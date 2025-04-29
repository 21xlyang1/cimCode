import os
import cv2
import argparse
import torch
import datetime
import asyncio
import collections
import json
import threading
import requests  # 用于发送 HTTP 请求
from ownutils.roimanager import ROIManager
from ownutils.inference import judge_point_rois
from ownutils.yolomodel import YoloModel
from getRTSP import get_rtsp_url_by_id
from websocket import start_server, broadcast_custom_message, broadcast_custom_message2

# 设置日志
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ReminderTime = [0, 0, 0]
LevelTime = 10
curRtsp = [""] * 35  # 用于存储每个摄像头的 RTSP URL

# 定义更新数据库的 URL
UPDATE_URL = "http://103.242.3.44:5020/user/updataFlowPath"  # 这里应该是完整的 URL

def config_paras():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default="test01.mp4", help='测试图像文件夹或视频或摄像头')
    parser.add_argument('--output', type=str, default="./output/", help='保存结果图像的文件夹，不能使用输入文件夹')
    parser.add_argument('--weights', type=str, default='./weights/yolov5s.pt', help='权重文件路径')
    parser.add_argument('--img_size', type=int, default=640, help='推理大小（像素）')
    parser.add_argument('--conf_thres', type=float, default=0.5, help='目标置信度阈值')
    parser.add_argument('--iou_thres', type=float, default=0.4, help='NMS的IOU阈值')
    parser.add_argument('--device', default='0', help='cuda设备，例如0或0,1,2,3或cpu')
    parser.add_argument('--classes', default=0, type=int, help='按类别过滤：--class 0，或--class 0 1 2 3')
    yolo5_config = parser.parse_args()
    return yolo5_config

def process_camera(camera_id, yolomodel):
    video_capture = cv2.VideoCapture(get_rtsp_url_by_id(camera_id))
    if not video_capture.isOpened():
        logging.error(f"Failed to open camera {camera_id}")
        return

    logging.info(f"Processing camera {camera_id}")

    # 记录开始时间
    start_time = datetime.datetime.now()
    max_people_count = 0
    detection_times = 0

    while True:
        try:
            ret, frame = video_capture.read()
            if not ret:
                logging.warning(f"Failed to read frame from camera {camera_id}")
                new_rtsp = get_rtsp_url_by_id(camera_id)
                if curRtsp[camera_id - 1] != new_rtsp:
                    logging.info(f"RTSP URL changed for camera {camera_id} from {curRtsp[camera_id - 1]} to {new_rtsp}")
                    curRtsp[camera_id - 1] = new_rtsp
                    video_capture.release()  # 释放旧的视频捕获对象
                    video_capture = cv2.VideoCapture(new_rtsp)  # 创建新的视频捕获对象
                    start_time = datetime.datetime.now()  # 更新开始时间
                continue

            # 检测当前帧中的行人
            bodies = yolomodel.detect_yolo(frame=frame, imgsize=640)
            person_count = len(bodies)  # 计算检测到的人数
            # logging.info(f"Camera {camera_id} detected {person_count} people")

            # 更新最大人数和检测次数
            max_people_count = max(max_people_count, person_count)
            detection_times += 1

            # 每 3 分钟更新 RTSP URL
            if (datetime.datetime.now() - start_time).total_seconds() > 60:
                # 发送更新请求
                update_database(camera_id, max_people_count, detection_times)

                # 重置计数器
                max_people_count = 0
                detection_times = 0
                start_time = datetime.datetime.now()  # 更新开始时间

            # 让出控制权
            asyncio.sleep(0)

        except Exception as e:
            logging.error(f"Error in camera {camera_id}: {e}")
            break

    video_capture.release()

def update_database(camera_id, max_people_count, detection_times):
    # 发送 POST 请求更新数据库
    payload = {
        "cameraId": camera_id,
        "peopleNum": max_people_count,
        "DetectionTimes": detection_times,
    }
    try:
        response = requests.post(UPDATE_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("isSuccess"):
                logging.info(f"Successfully updated database for camera {camera_id}: {result.get('msg')}")
            else:
                logging.error(f"Failed to update database for camera {camera_id}: {result.get('msg')}")
        else:
            logging.error(f"Error response from server for camera {camera_id}: {response.status_code}")
    except Exception as e:
        logging.error(f"Failed to send request for camera {camera_id}: {e}")

async def main():
    yolov5_config = config_paras()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logging.info(f"Using device: {device}")
    rm = ROIManager()
    rm.load_rois_from_json('rois.json')
    yolomodel = YoloModel(device, confthres=yolov5_config.conf_thres, iouthres=yolov5_config.iou_thres,
                          weight=yolov5_config.weights, classes=yolov5_config.classes)
    yolomodel.load_model()

    threads = []
    for i in range(1, 36):
        rtsp_url = get_rtsp_url_by_id(i)
        curRtsp[i - 1] = rtsp_url
        thread = threading.Thread(target=process_camera, args=(i, yolomodel))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # 等待所有线程完成

if __name__ == '__main__':
    # 启动 WebSocket 服务器
    # asyncio.run(start_server())  # 确保 start_server 是一个异步函数
    asyncio.run(main())
    logging.info("Starting event loop")
