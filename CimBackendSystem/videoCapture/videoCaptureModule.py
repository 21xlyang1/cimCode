import threading
import time
from logManager.log import videoCaptureLogger

import os
import cv2
import argparse
import torch
import datetime
from videoCapture.ownutils.roimanager import ROIManager
from videoCapture.ownutils.yolomodel import YoloModel
from getRTSP import get_rtsp_url_by_id

logger = videoCaptureLogger


class VideoCaptureModule(threading.Thread):
    def __init__(self):
        """
        初始化视频捕获模块。

        参数:
        rtsp_url (str): RTSP 流的 URL。
        frame_queue (Queue): 存放视频帧的队列。
        """
        super().__init__()
        # self.rtsp_url = rtsp_url
        # self.frame_queue = frame_queue
        # self.cap = cv2.VideoCapture(rtsp_url)
        # self.cameraId=cameraId
        self.videoNum=30
        self.running = True
        self.last_heartbeat = time.time()

    def config_paras(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--input', type=str, default="test01.mp4", help='test imgs folder or video or camera')
        parser.add_argument('--output', type=str, default="./output/",
                            help='folder to save result imgs, can not use input folder')
        parser.add_argument('--weights', type=str, default='./weights/yolov5s.pt', help='weights.pt path(s)')
        parser.add_argument('--img_size', type=int, default=640, help='inference size (pixels)')
        parser.add_argument('--conf_thres', type=float, default=0.5, help='object confidence threshold')
        parser.add_argument('--iou_thres', type=float, default=0.4, help='IOU threshold for NMS')
        parser.add_argument('--device', default='0', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
        parser.add_argument('--classes', default=0, type=int, help='filter by class: --class 0, or --class 0 1 2 3')
        yolo5_config = parser.parse_args()
        return yolo5_config

    def run(self):
        """
        运行视频捕获模块，读取视频帧并将其放入队列中。
        """
        # try:
        #     while self.running:
        #         ret, frame = self.cap.read()
        #         if ret:
        #             if self.frame_queue.full():
        #                 self.frame_queue.get()  # 丢弃最旧的帧
        #             self.frame_queue.put(frame)
        #             self.last_heartbeat = time.time()
        #         else:
        #             logger.error("Failed to capture frame")
        #             break
        # except Exception as e:
        #     logger.error(f"Exception in VideoCaptureModule: {e}")
        # finally:
        #     self.cap.release()
        logger.info("开始加载模型")
        yolov5_config = self.config_paras()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(device)
        rm = ROIManager()
        rm.load_rois_from_json('rois.json')
        yolomodel = YoloModel(device, confthres=yolov5_config.conf_thres, iouthres=yolov5_config.iou_thres,
                              weight=yolov5_config.weights, classes=yolov5_config.classes)
        yolomodel.load_model()
        logger.info("开始初始化视频流")
        video_captures = []
        for i in range(self.videoNum):
            url=get_rtsp_url_by_id(i)
            if url==None:
                logger.warning("加载第" + str(i) + "个摄像头失败")
            else:
                logger.info("加载第" + str(i) + "个摄像头，rul：[ " + url + " ]")
            video_captures.append(cv2.VideoCapture(url))

        mkfile_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        output_filename = str(mkfile_time) + ".mp4"
        output_path = os.path.join(yolov5_config.output, output_filename)
        print(f"Attempting to save video to: {output_path}")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_width = int(video_captures[1].get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(video_captures[1].get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (video_width, video_height), True)
        cv2.namedWindow('image')

        logger.info("开始获取监控图片")
        cut = 1
        while True:
            try:
                start_time = datetime.datetime.now()
                cut += 1
                ret, frame = video_captures[cut % self.videoNum].read()
                if not ret:
                    logger.warning("第"+str(cut % self.videoNum)+"摄像头的图片获取失败")
                    continue
                cv2.imshow('image', frame)
                logger.warning("第" + str(cut % self.videoNum) + "摄像头的图片获取成功")
                # if cut%100==0:
                #     r=get_rtsp_url_by_id(18)
                #     if curRtsp!=r:
                #         print("原地址：",curRtsp)
                #         print("现地址：",r)
                #         curRtsp=r
                #         video_capture = cv2.VideoCapture(curRtsp)

                # bodies = yolomodel.detect_yolo(frame=frame, imgsize=640)
                # frame = rm.draw_rois(frame)
                # frame, level = judge_point_rois(frame, bodies, rm)
                #
                # if level != 0:
                #     for i in range(level):
                #         if ReminderTime[i] == 0:
                #             await Reminder(i + 1)
                #         ReminderTime[i] = LevelTime
                #
                # cv2.imshow('image', frame)
                # end_time = datetime.datetime.now()
                # elapsed_time = (end_time - start_time).total_seconds()
                # print(f"Time taken to process frame: {elapsed_time:.6f} seconds")
                #
                #
                # for i in range(3):
                #     ReminderTime[i] -= elapsed_time
                #     if ReminderTime[i] < 0:
                #         ReminderTime[i] = 0

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
            except Exception as e:
                print(f"Error: {e}")


    def stop(self):
        """
        停止视频捕获模块。
        """
        self.running = False

    def get_heartbeat(self):
        """
        获取最后一次心跳时间戳。

        返回:
        last_heartbeat (float): 最后一次心跳的时间戳。
        """
        return self.last_heartbeat


if __name__ == '__main__':
    vcm=VideoCaptureModule()
    vcm.start()