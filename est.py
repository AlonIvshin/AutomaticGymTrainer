import time

import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
from enum import Enum
# Ofir
from threading import Thread

# Defines
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
FRONT_CAMERA_ID = 0
SIDE_CAMERA_ID = 1


class E_ExerciseInstructionType(Enum):
    STATIC = 0
    DYNAMIC = 1


class E_AlertDeviationTrigger(Enum):
    POSITIVE = 1
    BOTH = 0
    NEGATIVE = -1


class E_InstructionAxis(Enum):
    XY = 1
    XZ = 2
    YZ = 3


class ExerciseInstruction:
    def __init__(self, exerciseInstructionId, exerciseId, instructionId, alertId,
                 deviationPositive, deviationNegative, instructionStage, exerciseInstructionType,
                 alertDeviationTrigger) -> None:
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
    def __init__(self, instructionId, vertex1, vertex2, vertex3, angle, description, instructionAxis) -> None:
        self.instructionId = instructionId
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.vertex3 = vertex3
        self.angle = angle
        self.description = description
        self.instructionAxis = instructionAxis


# Ofir - Threaded cameras
class ThreadedCamera:
    def __init__(self, camID):

        self.capture = cv2.VideoCapture(camID)

        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True  # ofir
        self.thread.start()

        self.status = False
        self.frame = None

    def update(self):
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()

    def grab_frame(self):
        if self.status:
            return self.frame
        return None


# Dummy exercise data:
exerciseInstructionId = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
exerciseId = 1
exercise_stages = 2
deviationPositive = [7, 7, 7, 7, 8, 20, 20, 70, 70, 70, 70, 25, 25, 25, 25]
deviationNegative = [-7, -7, -7, -7, -8, -20, -20, -25, -25, -25, -25, -70, -70, -70, -70]
instructionStage = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]

exerciseInstructionType = [E_ExerciseInstructionType.STATIC.value, E_ExerciseInstructionType.STATIC.value,
                           E_ExerciseInstructionType.STATIC.value, E_ExerciseInstructionType.STATIC.value,
                           E_ExerciseInstructionType.STATIC.value, E_ExerciseInstructionType.STATIC.value
    , E_ExerciseInstructionType.STATIC.value, E_ExerciseInstructionType.DYNAMIC.value,
                           E_ExerciseInstructionType.DYNAMIC.value, E_ExerciseInstructionType.DYNAMIC.value,
                           E_ExerciseInstructionType.DYNAMIC.value, E_ExerciseInstructionType.DYNAMIC.value,
                           E_ExerciseInstructionType.DYNAMIC.value, E_ExerciseInstructionType.DYNAMIC.value,
                           E_ExerciseInstructionType.DYNAMIC.value]

alertDeviationTrigger = [E_AlertDeviationTrigger.BOTH.value, E_AlertDeviationTrigger.BOTH.value,
                         E_AlertDeviationTrigger.BOTH.value,
                         E_AlertDeviationTrigger.BOTH.value, E_AlertDeviationTrigger.BOTH.value,
                         E_AlertDeviationTrigger.BOTH.value,
                         E_AlertDeviationTrigger.BOTH.value, E_AlertDeviationTrigger.NEGATIVE.value,
                         E_AlertDeviationTrigger.NEGATIVE.value,
                         E_AlertDeviationTrigger.NEGATIVE.value, E_AlertDeviationTrigger.NEGATIVE.value,
                         E_AlertDeviationTrigger.POSITIVE.value,
                         E_AlertDeviationTrigger.POSITIVE.value, E_AlertDeviationTrigger.POSITIVE.value,
                         E_AlertDeviationTrigger.POSITIVE.value]

instructionId = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
vertex1 = [mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.LEFT_HIP,
           mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.LEFT_HIP,
           mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.RIGHT_ELBOW,
           mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST, mp_pose.PoseLandmark.RIGHT_ELBOW,
           mp_pose.PoseLandmark.RIGHT_WRIST, mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST,
           mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST]
vertex2 = [mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_HIP,
           mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.NOSE, mp_pose.PoseLandmark.LEFT_SHOULDER,
           mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW,
           mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.LEFT_SHOULDER,
           mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW]
vertex3 = [mp_pose.PoseLandmark.RIGHT_ANKLE, mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.LEFT_ANKLE,
           mp_pose.PoseLandmark.RIGHT_ANKLE, mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_SHOULDER,
           mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_SHOULDER,
           mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP,
           mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_SHOULDER]
angle = [175, 175, 90, 90, 15, 140, 140, 90, 90, 90, 90, 160, 160, 160, 160]
description = ""
# 1XY 2XZ 3YZ
instructionAxis = [E_InstructionAxis.XY.value, E_InstructionAxis.XY.value, E_InstructionAxis.XY.value,
                   E_InstructionAxis.XY.value, E_InstructionAxis.XY.value, E_InstructionAxis.XZ.value,
                   E_InstructionAxis.XZ.value, E_InstructionAxis.XY.value, E_InstructionAxis.XY.value,
                   E_InstructionAxis.XY.value, E_InstructionAxis.XY.value, E_InstructionAxis.XY.value,
                   E_InstructionAxis.XY.value, E_InstructionAxis.XY.value, E_InstructionAxis.XY.value]

instructions = []
exerciseInstructions = []

for id, v1, v2, v3, ang, axis in zip(instructionId, vertex1, vertex2, vertex3, angle, instructionAxis):
    instructions.append(Instruction(id, v1, v2, v3, ang, description, axis))

for eiid, id, devpos, devneg, istage, eitype, adt in zip(exerciseInstructionId,
                                                         instructionId, deviationPositive, deviationNegative,
                                                         instructionStage, exerciseInstructionType
        , alertDeviationTrigger):
    exerciseInstructions.append(ExerciseInstruction(eiid, 1, id, 0, devpos, devneg, istage, eitype, adt))
    # end of dummy data


def calculate_angle(vertex1, vertex2, vertex3, axis):
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


def my_est():
    # current stage variable
    current_stage = 0
    delay_duration = 0
    number_of_cameras = 0
    repetition_counter = 0
    repetition_direction = 1
    exercise_stage = None
    front_camera_thread = None
    side_camera_thread = None

    number_of_cameras = int(input("Enter the number of cameras you would like to use (1/2):"))
    front_camera_thread = ThreadedCamera(FRONT_CAMERA_ID)
    if number_of_cameras > 1:  # if the user selected more than 1 camera
        side_camera_thread = ThreadedCamera(SIDE_CAMERA_ID)

    #Testing bandwith fix
    #cv2.SetCaptureProperty(video1, cv.CV_CAP_PROP_FRAME_WIDTH, 800)
    time.sleep(1)
    start_time = datetime.now()
    diff = (datetime.now() - start_time).seconds  # converting into seconds
    while diff <= delay_duration:
        frame = front_camera_thread.grab_frame()
        if number_of_cameras > 1:
            side_frame = side_camera_thread.grab_frame()  # Camera #2 setup

        cv2.putText(frame, str(diff), (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                    cv2.LINE_AA)  # adding timer text
        cv2.imshow('Front Camera', frame)
        if number_of_cameras > 1:
            cv2.imshow('Side Camera ', side_frame)  # Camera 2 setup
        diff = (datetime.now() - start_time).seconds
        k = cv2.waitKey(10)

    front_camera_thread.capture.release()
    if number_of_cameras > 1:
        side_camera_thread.capture.release()  # Camera 2 setup

    cv2.destroyAllWindows()

    # Trainee setup stage has finished
    # Starting evaluation of posture
    #time.sleep(1)  # let the main thread sleep for 1 sec ofir
    # Both threads should be done by now (No cap is opened in this stage)

    front_camera_thread = ThreadedCamera(FRONT_CAMERA_ID)
    if number_of_cameras > 1:  # if the user selected more than 1 camera
        side_camera_thread = ThreadedCamera(SIDE_CAMERA_ID)
    time.sleep(1)
    # Exercise counter variables
    # Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.9, min_tracking_confidence=0.5) as front_pose,\
            mp_pose.Pose(min_detection_confidence=0.9, min_tracking_confidence=0.5) as side_pose:
        if number_of_cameras > 1:  # If True: enter 2 camera setup
            while True:
                frame = front_camera_thread.grab_frame()  # grab front camera frame
                side_frame = side_camera_thread.grab_frame()  # grab side camera frame
                # Recolor image to RGB
                # First camera
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Second camera
                side_image = cv2.cvtColor(side_frame, cv2.COLOR_BGR2RGB)
                side_image.flags.writeable = False

                # Make detection
                # First camera
                results = front_pose.process(image)
                # Second camera
                side_results = side_pose.process(side_image)

                # Recolor back to BGR
                # First camera
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                # Second camera
                side_image.flags.writeable = True
                side_image = cv2.cvtColor(side_image, cv2.COLOR_RGB2BGR)

                # Extract landmarks
                try:
                    landmarks = results.pose_landmarks.landmark  # Front Camera landmarks
                    side_landmarks = side_results.pose_landmarks.landmark  # Side Camera landmarks

                    # estimation each exercise instruction
                    v1 = v2 = v3 = 0
                    total_num_of_exercise_instructions_in_stage = 0
                    successful_exercise_instructions_in_current_stage = 0

                    for exercise_instruction_loop in exerciseInstructions:
                        # we are checking only instructions that match the current stage
                        if exercise_instruction_loop.instructionStage != current_stage and \
                                exercise_instruction_loop.instructionStage != 0:
                            continue

                        # get current instruction
                        current_instruction = instructions[exercise_instruction_loop.instructionId - 1]

                        # count exercise instructions
                        if exercise_instruction_loop.instructionStage != 0:
                            total_num_of_exercise_instructions_in_stage += 1

                        # Depth test, IF true -> XZ plain
                        if current_instruction.instructionAxis == E_InstructionAxis.XZ.value:  # Check instruction plain
                            v1 = [side_landmarks[current_instruction.vertex1.value].x,
                                  side_landmarks[current_instruction.vertex1.value].y,
                                  side_landmarks[current_instruction.vertex1.value].z]  # vertex 1 value
                            v2 = [side_landmarks[current_instruction.vertex2.value].x,
                                  side_landmarks[current_instruction.vertex2.value].y,
                                  side_landmarks[current_instruction.vertex2.value].z]  # vertex 2 value
                            v3 = [side_landmarks[current_instruction.vertex3.value].x,
                                  side_landmarks[current_instruction.vertex3.value].y,
                                  side_landmarks[current_instruction.vertex3.value].z]  # vertex 3 value
                        # Depth test, Else -> XY \ ZY plain
                        else:  # Camera 1 image analysis
                            v1 = [landmarks[current_instruction.vertex1.value].x,
                                  landmarks[current_instruction.vertex1.value].y,
                                  landmarks[current_instruction.vertex1.value].z]  # vertex 1 value
                            v2 = [landmarks[current_instruction.vertex2.value].x,
                                  landmarks[current_instruction.vertex2.value].y,
                                  landmarks[current_instruction.vertex2.value].z]  # vertex 2 value
                            v3 = [landmarks[current_instruction.vertex3.value].x,
                                  landmarks[current_instruction.vertex3.value].y,
                                  landmarks[current_instruction.vertex3.value].z]  # vertex 3 value

                        starting_angle = current_instruction.angle  # starting angle value
                        tested_angle = calculate_angle(v1, v2, v3,
                                                       current_instruction.instructionAxis)  # calculating the current angle

                        # searching for matching deviation trigger
                        if exercise_instruction_loop.alertDeviationTrigger == E_AlertDeviationTrigger.POSITIVE.value:
                            if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle:
                                print(f'Positive Deviation found, exercise instruction '
                                      f'{exercise_instruction_loop.exerciseInstructionId}')
                            if starting_angle + exercise_instruction_loop.deviationNegative >= tested_angle:
                                successful_exercise_instructions_in_current_stage += 1
                            continue
                        elif exercise_instruction_loop.alertDeviationTrigger == E_AlertDeviationTrigger.NEGATIVE.value:
                            if tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                                print(f'Negative Deviation found, exercise instruction '
                                      f'{exercise_instruction_loop.exerciseInstructionId}')
                            if starting_angle + exercise_instruction_loop.deviationPositive <= tested_angle:
                                successful_exercise_instructions_in_current_stage += 1
                            continue
                        elif exercise_instruction_loop.alertDeviationTrigger == E_AlertDeviationTrigger.BOTH.value:
                            if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle or \
                                    tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                                print(f'Deviation found, exercise instruction '
                                      f'{exercise_instruction_loop.exerciseInstructionId}')
                            continue

                    if successful_exercise_instructions_in_current_stage == total_num_of_exercise_instructions_in_stage:
                        current_stage += repetition_direction

                    if current_stage == exercise_stages:
                        if repetition_direction == 1:
                            repetition_counter += 1
                        repetition_direction = -1

                    elif current_stage == 0:
                        repetition_direction = 1

                    # Only for camera 1 atm
                    # Visualize angle
                    first = [side_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                             side_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y,
                             side_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].z]  # vertex 1 value
                    second = [side_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                              side_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
                              side_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z]  # vertex 2 value
                    third = [side_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             side_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
                             side_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z]  # vertex 3 value
                    displayed_angle = calculate_angle(first, second, third, E_InstructionAxis.XZ.value)

                    cv2.putText(side_image, str(displayed_angle),
                                tuple(np.multiply(second[0:2], [640, 480]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA
                                )


                # ofir
                except:
                    pass

                # Render exercise counter
                # Setup status box
                cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

                # Rep data
                cv2.putText(image, 'REPS', (15, 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, str(repetition_counter),
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
                cv2.putText(image, str(repetition_direction),
                            (110, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

                # Render detections
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                          )
                # Render detections - Camera 2 setup
                mp_drawing.draw_landmarks(side_image, side_results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                          )

                cv2.imshow('Mediapipe Feed Camera #1', image)
                cv2.imshow('Mediapipe Feed Camera #2', side_image)  # Camera 2 setup

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

        else:
            while True:
                frame = front_camera_thread.grab_frame()  # grab front camera frame
                # Recolor image to RGB
                # First camera
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                # First camera
                results = front_pose.process(image)

                # Recolor back to BGR
                # First camera
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Extract landmarks
                try:
                    landmarks = results.pose_landmarks.landmark  # Front Camera landmarks

                    # estimation each exercise instruction
                    v1 = v2 = v3 = 0
                    total_num_of_exercise_instructions_in_stage = 0
                    successful_exercise_instructions_in_current_stage = 0

                    for exercise_instruction_loop in exerciseInstructions:
                        # we are checking only instructions that match the current stage
                        if exercise_instruction_loop.instructionStage != current_stage and \
                                exercise_instruction_loop.instructionStage != 0:
                            continue

                        # get current instruction
                        current_instruction = instructions[exercise_instruction_loop.instructionId - 1]

                        # No depth
                        if current_instruction.instructionAxis != E_InstructionAxis.XY.value:
                            continue

                        # count exercise instructions
                        '''  if exercise_instruction_loop.instructionStage != 0:
                            total_num_of_exercise_instructions_in_stage += 1'''
                        total_num_of_exercise_instructions_in_stage += 1
                        v1 = [landmarks[current_instruction.vertex1.value].x,
                              landmarks[current_instruction.vertex1.value].y,
                              landmarks[current_instruction.vertex1.value].z]  # vertex 1 value
                        v2 = [landmarks[current_instruction.vertex2.value].x,
                              landmarks[current_instruction.vertex2.value].y,
                              landmarks[current_instruction.vertex2.value].z]  # vertex 2 value
                        v3 = [landmarks[current_instruction.vertex3.value].x,
                              landmarks[current_instruction.vertex3.value].y,
                              landmarks[current_instruction.vertex3.value].z]  # vertex 3 value

                        starting_angle = current_instruction.angle  # starting angle value
                        tested_angle = calculate_angle(v1, v2, v3,
                                                       current_instruction.instructionAxis)  # calculating the current angle

                        # searching for matching deviation trigger
                        if exercise_instruction_loop.alertDeviationTrigger == E_AlertDeviationTrigger.POSITIVE.value:
                            if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle:
                               ''' print(f'Positive Deviation found, exercise instruction '
                                      f'{exercise_instruction_loop.exerciseInstructionId}')'''
                            if starting_angle + exercise_instruction_loop.deviationNegative >= tested_angle:
                                successful_exercise_instructions_in_current_stage += 1
                            continue
                        elif exercise_instruction_loop.alertDeviationTrigger == E_AlertDeviationTrigger.NEGATIVE.value:
                            if tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                              '''  print(f'Negative Deviation found, exercise instruction '
                                      f'{exercise_instruction_loop.exerciseInstructionId}')'''
                            if starting_angle + exercise_instruction_loop.deviationPositive <= tested_angle:
                                successful_exercise_instructions_in_current_stage += 1
                            continue
                        elif exercise_instruction_loop.alertDeviationTrigger == E_AlertDeviationTrigger.BOTH.value:
                            if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle or \
                                    tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                              '''  print(f'Deviation found, exercise instruction '
                                      f'{exercise_instruction_loop.exerciseInstructionId}')'''
                            else:
                                successful_exercise_instructions_in_current_stage+=1
                            continue

                    if successful_exercise_instructions_in_current_stage == total_num_of_exercise_instructions_in_stage:
                        current_stage += repetition_direction




                    if current_stage == exercise_stages:
                        if repetition_direction == 1:
                            repetition_counter += 1
                        repetition_direction = -1

                    elif current_stage == 0:
                        repetition_direction = 1
                        print("current stage " + current_stage)
                        print("11111111111111111111")

                    # Visualize angle
                    first = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                             landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y,
                             landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].z]  # vertex 1 value
                    second = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z]  # vertex 2 value
                    third = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z]  # vertex 3 value

                    '''displayed_angle = calculate_angle(first, second, third, E_InstructionAxis.XZ.value)
                    
                    cv2.putText(image, str(displayed_angle),
                                tuple(np.multiply(second[0:2], [640, 480]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA
                                )'''


                # ofir
                except:
                    pass

                # Render exercise counter
                # Setup status box
                cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

                # Rep data
                cv2.putText(image, 'REPS', (15, 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, str(repetition_counter),
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
                cv2.putText(image, str(repetition_direction),
                            (110, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

                # Render detections
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                          )

                cv2.imshow('Mediapipe Feed Camera #1', image)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break


        front_camera_thread.capture.release()
        if number_of_cameras > 1:
            side_camera_thread.capture.release()  # Camera 2 setup
        cv2.destroyAllWindows()


my_est()
