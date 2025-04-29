import os
import cv2
import argparse
import torch
import datetime
import asyncio
import collections
from ownutils.roimanager import ROIManager
from ownutils.inference import judge_point_rois
from ownutils.yolomodel import YoloModel
from websocket import broadcast_custom_message, start_server
from getRTSP import get_rtsp_url_by_id

# 设置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ReminderTime = [0, 0, 0]
LevelTime = 10
curRtsp = ""

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

async def main():
    yolov5_config = config_paras()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logging.info(f"Using device: {device}")
    rm = ROIManager()
    rm.load_rois_from_json('rois.json')
    yolomodel = YoloModel(device, confthres=yolov5_config.conf_thres, iouthres=yolov5_config.iou_thres, weight=yolov5_config.weights, classes=yolov5_config.classes)
    yolomodel.load_model()

    curRtsp = get_rtsp_url_by_id(18)
    video_capture = cv2.VideoCapture(curRtsp)
    video_captures = [cv2.VideoCapture(get_rtsp_url_by_id(18 + i)) for i in range(5)]

    # 设置视频输出
    mkfile_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_filename = str(mkfile_time) + ".mp4"
    output_path = os.path.join(yolov5_config.output, output_filename)
    logging.info(f"Attempting to save video to: {output_path}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (video_width, video_height), True)
    cv2.namedWindow('image')

    # 缓存视频帧
    frame_buffer = collections.deque(maxlen=200)  # 假设视频帧率为20帧/秒，缓存10秒的帧

    cut = 1
    while True:
        try:
            start_time = datetime.datetime.now()
            cut += 1
            ret, frame = video_capture.read()
            if not ret:
                logging.warning("Failed to read frame from video capture")
                continue

            if cut % 100 == 0:
                new_rtsp = get_rtsp_url_by_id(18)
                if curRtsp != new_rtsp:
                    logging.info(f"RTSP URL changed from {curRtsp} to {new_rtsp}")
                    curRtsp = new_rtsp
                    video_capture = cv2.VideoCapture(curRtsp)

            bodies = yolomodel.detect_yolo(frame=frame, imgsize=640)
            frame = rm.draw_rois(frame)
            frame, level = judge_point_rois(frame, bodies, rm)

            current_time = datetime.datetime.now()
            frame_buffer.append((current_time, frame))

            if level != 0:
                for i in range(level):
                    if ReminderTime[i] == 0:
                        await Reminder(i + 1)
                        save_video_clip(frame_buffer, video_capture, 5, yolov5_config.output)
                    ReminderTime[i] = LevelTime

            cv2.imshow('image', frame)
            end_time = datetime.datetime.now()
            elapsed_time = (end_time - start_time).total_seconds()
            logging.info(f"Time taken to process frame: {elapsed_time:.6f} seconds")

            for i in range(3):
                ReminderTime[i] -= elapsed_time
                if ReminderTime[i] < 0:
                    ReminderTime[i] = 0

            await asyncio.sleep(0)  # 让出控制权

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        except Exception as e:
            logging.error(f"Error: {e}")

    video_capture.release()
    out.release()
    cv2.destroyAllWindows()

async def Reminder(level):
    reminder_message = {"alert": f"Level {level} intrusion"}
    logging.info(f"有行人进入{level}级围栏")
    await broadcast_custom_message(level)

def save_video_clip(frame_buffer, video_capture, seconds, output_dir):
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(seconds=seconds)
    end_time = current_time + datetime.timedelta(seconds=seconds)

    frames_to_save = [frame for timestamp, frame in frame_buffer if start_time <= timestamp <= end_time]

    mkfile_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_filename = f"drowning_event_{mkfile_time}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    logging.info(f"Saving drowning event video to: {output_path}")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (video_width, video_height), True)

    for frame in frames_to_save:
        out.write(frame)

    out.release()

if __name__ == '__main__':
    loop = start_server()
    loop.create_task(main())
    logging.info("Starting event loop")
    loop.run_forever()
