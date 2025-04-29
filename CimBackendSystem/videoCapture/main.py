# from objectPool import ObjectPoolManager
# from heartbeatMonitor import HeartbeatMonitor
# from config import FRAME_QUEUE_SIZE, HEARTBEAT_INTERVAL
#
#
#
#
#
#
# def main1():
#     """
#     主程序，初始化并启动对象池管理器和心跳监测器。
#     """
#     frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
#
#     # 初始化对象池管理器
#     object_pool_manager = ObjectPoolManager(frame_queue)
#     object_pool_manager.start()
#
#     # 初始化心跳监测器
#     heartbeat_monitor = HeartbeatMonitor(object_pool_manager.capture_modules, HEARTBEAT_INTERVAL)
#     heartbeat_monitor.start()
#
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#
#         object_pool_manager.stop()
#         heartbeat_monitor.stop()



import os
import cv2
import argparse
import torch
import datetime
import asyncio
from videoCapture.ownutils.roimanager import ROIManager
from videoCapture.ownutils.yolomodel import YoloModel
from websocket import broadcast_custom_message, start_server
from getRTSP import get_rtsp_url_by_id
from logManager.log import setup_logger

ReminderTime = [0, 0, 0]
LevelTime = 10
curRtsp=""
videoCaptureLog=setup_logger("videoCapture")
def config_paras():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default="test01.mp4", help='test imgs folder or video or camera')
    parser.add_argument('--output', type=str, default="./output/", help='folder to save result imgs, can not use input folder')
    parser.add_argument('--weights', type=str, default='./weights/yolov5s.pt', help='weights.pt path(s)')
    parser.add_argument('--img_size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf_thres', type=float, default=0.5, help='object confidence threshold')
    parser.add_argument('--iou_thres', type=float, default=0.4, help='IOU threshold for NMS')
    parser.add_argument('--device', default='0', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--classes', default=0, type=int, help='filter by class: --class 0, or --class 0 1 2 3')
    yolo5_config = parser.parse_args()
    return yolo5_config

async def main():
    yolov5_config = config_paras()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(device)
    rm = ROIManager()
    rm.load_rois_from_json('rois.json')
    yolomodel = YoloModel(device, confthres=yolov5_config.conf_thres, iouthres=yolov5_config.iou_thres, weight=yolov5_config.weights, classes=yolov5_config.classes)
    yolomodel.load_model()

    curRtsp=get_rtsp_url_by_id(18)
    video_capture = cv2.VideoCapture(curRtsp)
    video_captures=[]
    for i in range(30):
        print("dfads")
        video_captures.append(cv2.VideoCapture(get_rtsp_url_by_id(i)))


    # mkfile_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # output_filename = str(mkfile_time) + ".mp4"
    # output_path = os.path.join(yolov5_config.output, output_filename)
    # print(f"Attempting to save video to: {output_path}")
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    # video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # out = cv2.VideoWriter(output_path, fourcc, 20.0, (video_width, video_height), True)
    # cv2.namedWindow('image')
    #
    # while True:
    #     # print(get_rtsp_url_by_id(18))
    #     try:
    #         ret, frame = video_capture.read()
    #         if not ret:
    #             break
    #         cv2.imshow('image', frame)
    #     except Exception as e:
    #         print(f"Error: {e}")
    # return

    # video_capture=cv2.VideoCapture("test01.mp4")

    mkfile_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_filename = str(mkfile_time) + ".mp4"
    output_path = os.path.join(yolov5_config.output, output_filename)
    print(f"Attempting to save video to: {output_path}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (video_width, video_height), True)
    cv2.namedWindow('image')

    cut = 1
    while True:
        # print(get_rtsp_url_by_id(18))
        try:
            start_time = datetime.datetime.now()
            cut += 1
            ret, frame = video_captures[cut%30].read()
            if not ret:
                print("第",cut%30,"摄像头失效")
                continue
            cv2.imshow('image', frame)
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

            await asyncio.sleep(0)  # 让出控制权

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        except Exception as e:
            print(f"Error: {e}")


    video_capture.release()
    out.release()
    cv2.destroyAllWindows()

async def Reminder(level):

    reminder_message = {"alert": f"Level {level} intrusion"}
    # await asyncio.sleep(10)  # 等待10秒后发送自定义广播消息
    print("有行人进入" + str(level) + "级围栏")
    # message = json.dumps({"Level": f"{level}","Place":"陇中九巷1号"})
    await broadcast_custom_message(level)

if __name__ == '__main__':
    loop = start_server()
    loop.create_task(main())
    print("1")
    loop.run_forever()