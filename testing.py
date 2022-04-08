import cv2
import numpy as np
from Utils import DBConnection as DB

import urllib


''' Working image extraction from URL in DB'''

image_links = DB.getExerciseImages(1)
#print(image_links)
#img = io.imread('https://raw2.github.com/scikit-image/scikit-image.github.com/master/_static/img/logo.png')
url = image_links[0][0]
url_response = urllib.request.urlopen(url)
img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
img = cv2.imdecode(img_array, -1)
cv2.imshow('URL Image', img)
cv2.waitKey()

''' END '''



counter = 0
current_stage = 0
rep_direction = 1

image = np.zeros((512,256,3), np.uint8)


cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

# Rep data
cv2.putText(image, 'REPS', (15, 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
cv2.putText(image, str(counter),
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

# Stage data
cv2.putText(image, 'STAGE', (65, 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
cv2.putText(image, str(current_stage),
            (60, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

cv2.putText(image, 'STATE', (115, 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
cv2.putText(image, str(rep_direction),
            (110, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)


cv2.putText(image, "Alerts",(15, 150),cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)


cv2.imshow("My image",image)

while True:
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break