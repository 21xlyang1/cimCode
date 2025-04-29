import cv2
from PIL import Image

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

image_path = 'img/1.jpeg'
image = cv2.imread(image_path)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

for (x, y, w, h) in faces:
    face_region = image[y:y+h, x:x+w]
    face_region = cv2.GaussianBlur(face_region, (99, 99), 30)
    image[y:y+h, x:x+w] = face_region

output_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
output_image.save('output_image.jpg')

output_image.show()








