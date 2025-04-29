import cv2
import torch
import numpy as np
from utils.datasets import letterbox
from utils.utils import non_max_suppression


def img_preprocessing(np_img,device,newsize=640):
    np_img=letterbox(np_img,new_shape=newsize)[0]
    np_img = np_img[:, :, ::-1].transpose(2, 0, 1)
    np_img = np.ascontiguousarray(np_img)
    if device == "cuda":
        tensor_img=torch.from_numpy(np_img).to(device)
    else:
        tensor_img = torch.from_numpy(np_img)
    tensor_img=tensor_img[np.newaxis,:].float()
    tensor_img /= 255.0
    return tensor_img


def yolov5_prediction(model,tensor_img,conf_thres,iou_thres,classes):
    # print(classes)

    with torch.no_grad():
        out=model(tensor_img)[0]

        pred = non_max_suppression(out, conf_thres, iou_thres, classes=classes)[0]
    return pred

def judge_point(frame, bodies, roi):

    for i, det in enumerate(bodies):
        # print(f"i的值{i}, det的值{det}")
        x1, y1, x2, y2, conf, cls = det
        w = x2 - x1
        h = y2 - y1
        bottom_center_x = int(x1 + w // 2)
        bottom_center_y = int(y1 + h)
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.circle(frame, (bottom_center_x, bottom_center_y), 6, (0, 0, 255), -1)
        if cv2.pointPolygonTest(np.array(roi.vertices, dtype=np.int32), (bottom_center_x, bottom_center_y),
                                False) > 0:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    return frame


def judge_point_rois(frame, bodies, roi_manager):
    level=0
    for i, det in enumerate(bodies):
        x1, y1, x2, y2, conf, cls = det
        w = x2 - x1
        h = y2 - y1
        bottom_center_x = int(x1 + w // 2)
        bottom_center_y = int(y1 + h)
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)

        # 绘制原始人框
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(frame, (bottom_center_x, bottom_center_y), 6, (0, 0, 255), -1)

        level=3
        # 检查底部中心点是否在任意ROI内

        for vertices in roi_manager.roi_dict.values():
            if cv2.pointPolygonTest(np.array(vertices, dtype=np.int32), (bottom_center_x, bottom_center_y), False) > 0:
                break
            level-=1

        color = [(0, 255, 0), (0, 255, 255), (32, 165, 218),(0, 0, 255)]
        # 如果在ROI内，改变人框颜色为红色

        cv2.rectangle(frame, (x1, y1), (x2, y2), color[level], 2)

    return frame,level