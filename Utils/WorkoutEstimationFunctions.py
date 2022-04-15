import urllib
import cv2
import numpy as np
from ClassObjects.EnumClasses import E_InstructionAxis


def getImageFromLink(url):
    url_response = urllib.request.urlopen(url)
    img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, -1)
    return img


def calculateScore(deviation):
    return max(1, deviation / 10)


def calculateAngle(vertex1, vertex2, vertex3, axis):
    if axis == E_InstructionAxis.XY.value:
        vertex1 = [vertex1[0], vertex1[1]]
        vertex2 = [vertex2[0], vertex2[1]]
        vertex3 = [vertex3[0], vertex3[1]]
    elif axis == E_InstructionAxis.XZ.value:
        vertex1 = [vertex1[0], vertex1[2]]
        vertex2 = [vertex2[0], vertex2[2]]
        vertex3 = [vertex3[0], vertex3[2]]
    else:
        vertex1 = [vertex1[1], vertex1[2]]
        vertex2 = [vertex2[1], vertex2[2]]
        vertex3 = [vertex3[1], vertex3[2]]

    vertex1 = np.array(vertex1)  # First
    vertex2 = np.array(vertex2)  # Mid
    vertex3 = np.array(vertex3)  # End

    radians = np.arctan2(vertex3[1] - vertex2[1], vertex3[0] - vertex2[0]) - np.arctan2(vertex1[1] - vertex2[1],
                                                                                        vertex1[0] - vertex2[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle


'''
Types:
first,second - TriggeredAlert
return: True if equals, False otherwise
'''


def compareTraineeTriggeredAlerts(first, second):
    if first.alertId > second.alertId:
        return 1
    if first.alertId < second.alertId:
        return -1
    # alertId is equals in both sides
    if first.stageNumber > second.stageNumber:
        return 1
    if first.stageNumber < second.stageNumber:
        return -1
    # stageNumber is equal in both sides
    if first.repNumber > second.repNumber:
        return 1
    if first.repNumber < second.repNumber:
        return -1
    # both sides are the same element
    return 0
