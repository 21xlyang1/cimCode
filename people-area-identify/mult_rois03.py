import os
import cv2
import argparse
import torch
import datetime
from ownutils.roimanager import ROIManager
from ownutils.inference import  judge_point_rois
from ownutils.yolomodel import YoloModel

ReminderTime=[0,0,0]
LevelTime=10

def config_paras():

    parser = argparse.ArgumentParser()
    # 视频的路径，默认是本项目中的一个测试视频test.mp4，可自行更改
    parser.add_argument('--input', type=str, default="test01.mp4", help='test imgs folder or video or camera')   # 输入'0'表示调用电脑默认摄像头
    # 处理后视频的输出路径
    parser.add_argument('--output', type=str, default="./output/", help='folder to save result imgs, can not use input folder')
    parser.add_argument('--weights', type=str, default='./weights/yolov5s.pt', help='weights.pt path(s)')
    parser.add_argument('--img_size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf_thres', type=float, default=0.5, help='object confidence threshold')
    parser.add_argument('--iou_thres', type=float, default=0.4, help='IOU threshold for NMS')
    # GPU（0表示设备的默认的显卡）或CPU
    parser.add_argument('--device', default='0', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    # 通过classes来过滤yolo要检测类别，0表示检测人，1表示自行车，更多具体类别数字可以在19行附近打印出来
    parser.add_argument('--classes', default=0, type=int, help='filter by class: --class 0, or --class 0 1 2 3')

    yolo5_config = parser.parse_args()

    # print(yolo5_config)  # 查看配置选项

    return yolo5_config


def main():

    yolov5_config = config_paras()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # device='cpu'
    print(device)
    rm = ROIManager()
    rm.load_rois_from_json('rois.json')

    yolomodel = YoloModel(device, confthres=yolov5_config.conf_thres, iouthres=yolov5_config.iou_thres, weight=yolov5_config.weights, classes=yolov5_config.classes)
    yolomodel.load_model()

    # 加载视频
    video_capture = cv2.VideoCapture(yolov5_config.input)
    mkfile_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_filename = str(mkfile_time) + ".mp4"
    output_path = os.path.join(yolov5_config.output, output_filename)
    print(f"Attempting to save video to: {output_path}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (video_width, video_height), True)
    cv2.namedWindow('image')

    while True:
        start_time = datetime.datetime.now()  # 记录开始时间
        ret, frame = video_capture.read()
        if not ret:
            break
        # print(ReminderTime)

        bodies = yolomodel.detect_yolo(frame=frame, imgsize=640)
        frame = rm.draw_rois(frame)
        frame,level = judge_point_rois(frame, bodies, rm)


        if level!=0:
            for i in range(level):
                if ReminderTime[i]==0:
                    Reminder(i+1)
                ReminderTime[i]=LevelTime




        # cv2.imshow('image', frame)
        # out.write(frame)
        end_time = datetime.datetime.now()  # 记录结束时间
        elapsed_time = (end_time - start_time).total_seconds()  # 计算经过的时间
        print(f"Time taken to process frame: {elapsed_time:.6f} seconds")  # 打印处理时间

        for i in range(3):
            ReminderTime[i]-=elapsed_time
            if ReminderTime[i]<0:
                ReminderTime[i]=0


        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break


    video_capture.release()
    out.release()
    cv2.destroyAllWindows()

def Reminder(level):
    print("有行人进入"+str(level)+"级围栏")
    # Sample.main(["陇中九巷1号", str(level)])

if __name__ == '__main__':
    main()
