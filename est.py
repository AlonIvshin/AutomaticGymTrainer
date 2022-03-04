import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
from enum import Enum

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


class E_ExerciseInstructionType(Enum):
    STATIC =  0
    DYNAMIC = 1


class E_AlertDeviationTrigger(Enum):
    POSITIVE = 1
    BOTH = 0
    NEGATIVE = -1

class ExerciseInstruction:
    def __init__(self,exerciseInstructionId,exerciseId,instructionId,alertId,
    deviationPositive,deviationNegative,instructionStage,exerciseInstructionType,alertDeviationTrigger) -> None:
         self.exerciseInstructionId = exerciseInstructionId
         self.exerciseId = exerciseId 
         self.instructionId = instructionId
         self.alertId = alertId
         self.deviationPositive = deviationPositive
         self.deviationNegative = deviationNegative
         self.instructionStage = instructionStage
         self.exerciseInstructionType = exerciseInstructionType
         self.alertDeviationTrigger = alertDeviationTrigger


class Instruction:
    def __init__(self,instructionId,vertex1,vertex2,vertex3,angle,description) -> None:
        self.instructionId = instructionId
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.vertex3 = vertex3
        self.angle = angle
        self.description = description

#Dummy exercise data:
exerciseInstructionId = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
exerciseId = 1
deviationPositive = [7,7,7,7,2,20,20,120,140,120,140,10,10,10,10]
deviationNegative = [-7,-7,-7,-7,-1,-20,-20,-10,-10,-10,-10,-120,-140,-120,-140] 
instructionStage = [0,0,0,0,0,0,0,1,1,1,1,2,2,2,2]

exerciseInstructionType = [E_ExerciseInstructionType.STATIC.value,E_ExerciseInstructionType.STATIC.value,
E_ExerciseInstructionType.STATIC.value,E_ExerciseInstructionType.STATIC.value,
E_ExerciseInstructionType.STATIC.value,E_ExerciseInstructionType.STATIC.value
,E_ExerciseInstructionType.STATIC.value,E_ExerciseInstructionType.DYNAMIC.value,
E_ExerciseInstructionType.DYNAMIC.value,E_ExerciseInstructionType.DYNAMIC.value,
E_ExerciseInstructionType.DYNAMIC.value,E_ExerciseInstructionType.DYNAMIC.value,
E_ExerciseInstructionType.DYNAMIC.value,E_ExerciseInstructionType.DYNAMIC.value,
E_ExerciseInstructionType.DYNAMIC.value]

alertDeviationTrigger = [E_AlertDeviationTrigger.BOTH.value,E_AlertDeviationTrigger.BOTH.value,E_AlertDeviationTrigger.BOTH.value,
E_AlertDeviationTrigger.BOTH.value,E_AlertDeviationTrigger.BOTH.value,E_AlertDeviationTrigger.BOTH.value,
E_AlertDeviationTrigger.BOTH.value,E_AlertDeviationTrigger.NEGATIVE.value,E_AlertDeviationTrigger.NEGATIVE.value,
E_AlertDeviationTrigger.NEGATIVE.value,E_AlertDeviationTrigger.NEGATIVE.value,E_AlertDeviationTrigger.POSITIVE.value,
E_AlertDeviationTrigger.POSITIVE.value,E_AlertDeviationTrigger.POSITIVE.value,E_AlertDeviationTrigger.POSITIVE.value]

instructionId = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
vertex1 = [mp_pose.PoseLandmark.RIGHT_HIP.value,mp_pose.PoseLandmark.LEFT_HIP.value,
mp_pose.PoseLandmark.RIGHT_HIP.value,mp_pose.PoseLandmark.LEFT_HIP.value,
mp_pose.PoseLandmark.LEFT_HIP.value,mp_pose.PoseLandmark.LEFT_ELBOW,mp_pose.PoseLandmark.RIGHT_ELBOW,
mp_pose.PoseLandmark.LEFT_ELBOW,mp_pose.PoseLandmark.LEFT_WRIST,mp_pose.PoseLandmark.RIGHT_ELBOW,
mp_pose.PoseLandmark.RIGHT_WRIST,mp_pose.PoseLandmark.LEFT_ELBOW,mp_pose.PoseLandmark.LEFT_WRIST,
mp_pose.PoseLandmark.RIGHT_ELBOW,mp_pose.PoseLandmark.RIGHT_WRIST]
vertex2 = [mp_pose.PoseLandmark.RIGHT_KNEE,mp_pose.PoseLandmark.LEFT_KNEE,mp_pose.PoseLandmark.LEFT_HIP,
mp_pose.PoseLandmark.RIGHT_HIP,mp_pose.PoseLandmark.NOSE,mp_pose.PoseLandmark.LEFT_SHOULDER,
mp_pose.PoseLandmark.RIGHT_SHOULDER,mp_pose.PoseLandmark.LEFT_SHOULDER,mp_pose.PoseLandmark.LEFT_ELBOW,
mp_pose.PoseLandmark.RIGHT_SHOULDER,mp_pose.PoseLandmark.RIGHT_ELBOW,mp_pose.PoseLandmark.LEFT_SHOULDER,
mp_pose.PoseLandmark.LEFT_ELBOW,mp_pose.PoseLandmark.RIGHT_SHOULDER,mp_pose.PoseLandmark.RIGHT_ELBOW]
vertex3 = [mp_pose.PoseLandmark.RIGHT_ANKLE,mp_pose.PoseLandmark.LEFT_ANKLE,mp_pose.PoseLandmark.LEFT_ANKLE,
mp_pose.PoseLandmark.RIGHT_ANKLE,mp_pose.PoseLandmark.RIGHT_HIP,mp_pose.PoseLandmark.RIGHT_SHOULDER,
mp_pose.PoseLandmark.LEFT_SHOULDER,mp_pose.PoseLandmark.LEFT_HIP,mp_pose.PoseLandmark.LEFT_SHOULER,
mp_pose.PoseLandmark.RIGHT_HIP,mp_pose.PoseLandmark.RIGHT_SHOULDER,mp_pose.PoseLandmark.LEFT_HIP,
mp_pose.PoseLandmark.LEFT_SHOULDER,mp_pose.PoseLandmark.RIGHT_HIP,mp_pose.PoseLandmark.RIGHT_SHOULDER]
angle = [170,170,90,90,11,180,180,45,30,45,30,165,170,165,170]
description = ""

instructions = []
exerciseInstructions = []

for id,v1,v2,v3,ang in zip(instructionId,vertex1,vertex2,vertex3,angle):
    instructions.append(Instruction(id,v1,v2,v3,ang,description))

for eiid,ei,id,devpos,devneg,istage,eitype,adt in zip(exerciseInstructionId,exerciseId,
    instructionId,deviationPositive,deviationNegative,instructionStage,exerciseInstructionType
    ,alertDeviationTrigger):
    exerciseInstructions.append(ExerciseInstruction(eiid,ei,id,0,devpos,devneg,istage,eitype,adt))
    #end of dummy data

def my_est(temp2):
    def calculate_angle(a, b, c):
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    cap = cv2.VideoCapture(0)

    # the duration (in seconds)
    duration = 1

    ret, frame = cap.read()
    start_time = datetime.now()
    diff = (datetime.now() - start_time).seconds  # converting into seconds
    while (diff <= duration):
        ret, frame = cap.read()
        cv2.putText(frame, str(diff), (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                    cv2.LINE_AA)  # adding timer text
        cv2.imshow('frame', frame)
        diff = (datetime.now() - start_time).seconds
        k = cv2.waitKey(10)

    cap.release()
    cv2.destroyAllWindows()

    cap = cv2.VideoCapture(0)
    # Curl counter variables
    counter = 0
    stage = None

    ## Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()

            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Make detection
            results = pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates
                shoulderLeft = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                nose = [landmarks[mp_pose.PoseLandmark.NOSE.value].x, landmarks[mp_pose.PoseLandmark.NOSE.value].y]
                shoulderRight = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                 landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

                #testing exercie instructions
                v1 = v2 =v3 =0
                for ei in exerciseInstructions:
                    v1 = ei.instructionid.

                # Calculate angle
                #angle = calculate_angle(shoulderLeft, nose, shoulderRight)

                # Visualize angle
               # cv2.putText(image, str(angle),
                            #tuple(np.multiply(nose, [640, 480]).astype(int)),
                            #cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA
                          #  )

                # Curl counter logic
                if angle > 160:
                    stage = "down"
                if angle < 30 and stage == 'down':
                    stage = "up"
                    counter += 1
                    print(counter)

            except:
                pass

            # Render curl counter
            # Setup status box
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
            cv2.putText(image, stage,
                        (60, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                      )

            cv2.imshow('Mediapipe Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
