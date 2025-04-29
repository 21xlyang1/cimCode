from videoCapture.utils.general import scale_coords
from videoCapture.models.experimental import attempt_load
from videoCapture.utils.general import non_max_suppression
from videoCapture.ownutils.inference import img_preprocessing



class YoloModel:
    def __init__(self, device, confthres, iouthres, weight, classes):
        self.name = "Yolo Model"
        self.model = None
        self.device = device
        self.classes = classes
        self.confthres = confthres
        self.iouthres = iouthres
        self.weight = weight

    def load_model(self):
        try:
            model = attempt_load(self.weight, map_location=self.device)
            self.model = model
            msg = str(self.name) + " load successfully."
        except Exception as e:
            msg = str(e) + " error occur."

        return msg

    # 直接返回检测到的结果
    def detect_yolo(self, frame, imgsize):
        # 图像预处理
        img = img_preprocessing(frame, self.device, imgsize)
        # 进行推理
        pred = self.model(img)[0]
        # 进行非极大值抑制
        pred = non_max_suppression(pred, self.confthres, self.iouthres, classes=self.classes)[0]
        # 将预测到的结果往原图形的尺寸上调整
        pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], frame.shape).round()

        # 返回值
        if pred is not None and len(pred) > 0:
            det = pred.cpu().numpy()
            return det
        else:
            return []
