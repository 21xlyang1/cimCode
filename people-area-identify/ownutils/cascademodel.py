import cv2


class CascadeModel:
    def __init__(self):
        self.name = "Cascade Model"
        self.path = "./weights/haarcascade_fullbody.xml"
        self.classifier = None

    def load_model(self):
        try:
            classifier = cv2.CascadeClassifier(self.path)
            self.classifier = classifier
            msg = str(self.name) + " load successfully."
        except Exception as e:
            msg = str(e) + " error occur."

        return msg

    def detect_cascade(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        outputs = self.classifier.detectMultiScale(gray, 1.1, 4)

        return outputs
