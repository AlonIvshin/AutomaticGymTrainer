import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
from enum import Enum
import psycopg2

# connect to the db
con = psycopg2.connect(
    host="127.0.0.1",
    database="mytrainer",
    user="postgres",
    password="root")

# cursor
cur = con.cursor()

# Ofir

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


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
        self.insAlertData = None

class Alerts:
    def __init__(self,alertid, aiid, alerttext) -> None:
        self.alertid = alertid
        self.aiid = aiid
        self.alerttext = alerttext


# Dummy exercise data:
exerciseId = 1

# extracting exercise instruction data from db:

# QUERY 1: getting all exercise's instruction data
cur.execute('''select e.exercise_instruction_id,e.instruction_id,e.alert_id,e.deviation_positive,e.deviation_negative,
e.instruction_stage,e.exercise_instruction_type,e.alert_deviation_trigger
from exercises_instructions as e
where e.exercise_id = %s''', str(exerciseId))
res = cur.fetchall()
exerciseInstructionId, iid1, alertids, deviationPositive, deviationNegative, instructionStage, exerciseInstructionType, \
alertDeviationTrigger = zip(*res)

# QUERY 2: getting exercise's stages number
cur = con.cursor()
cur.execute('select num_of_stages from exercises where exercise_id = %s', str(exerciseId))
res = cur.fetchall()
exercise_stages = res[0][0]

# QUERY 3: getting all instruction's data of the exercise
cur.execute('''select i.instruction_id,i.vertex1,i.vertex2,i.vertex3,i.angle,i.description,i.instruction_axis
from instructions as i
inner join exercises_instructions as ei on i.instruction_id=ei.instruction_id
where ei.exercise_id = %s''', str(exerciseId))
res = cur.fetchall()
instructionId, vertex1, vertex2, vertex3, angle, description, instructionAxis = zip(*res)  # instruction's columns

# QUERY 4: getting all alert's data of the exercise
cur.execute('''select a.alert_id,a.instruction_id,a.alert_text
from alerts as a
inner join exercises_instructions as ei on a.instruction_id=ei.instruction_id
where ei.exercise_id = %s''', str(exerciseId))
res = cur.fetchall()
alertids2, aiid, alerttext = zip(*res)

instructions = []
exerciseInstructions = []
insAlertData = []

#creating alerts objects
for ai,iid,at in zip(alertids2,aiid,alerttext):
    insAlertData.append(Alerts(ai,iid,at))

# creating instructions and exerciseInstructions objects
for id, v1, v2, v3, ang, axis in zip(instructionId, vertex1, vertex2, vertex3, angle, instructionAxis):
    instructions.append(Instruction(id, v1, v2, v3, ang, description, axis))


for item in insAlertData:
    instructions[item.aiid - 1].insAlertData = item

for eiid, id, devpos, devneg, istage, eitype, adt in zip(exerciseInstructionId,
                                                         instructionId, deviationPositive, deviationNegative,
                                                         instructionStage, exerciseInstructionType
        , alertDeviationTrigger):
    exerciseInstructions.append(ExerciseInstruction(eiid, 1, id, 0, devpos, devneg, istage, eitype, adt))
    # end of dummy data

    # close cursor
    cur.close()
    # close connection
    con.close()
    # print()


def my_est():
    # current stage variable
    current_stage = 0

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

    cap = cv2.VideoCapture(0)


    # the duration (in seconds)
    duration = 2

    ret, frame = cap.read()
    start_time = datetime.now()
    diff = (datetime.now() - start_time).seconds  # converting into seconds
    while (diff <= duration):
        ret, frame = cap.read()
        imS = cv2.resize(frame, (1024, 768))  # Resize image
        cv2.putText(frame, str(diff), (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                    cv2.LINE_AA)  # adding timer text
        cv2.imshow('frame', imS)
        diff = (datetime.now() - start_time).seconds
        k = cv2.waitKey(10)

    cap.release()
    cv2.destroyAllWindows()

    cap = cv2.VideoCapture(0)


    # Curl counter variables
    counter = 0
    stage = None
    time_c = 0
    rep_direction = 1
    ## Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.9, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            current_set = set()
            current_list = []
            # Make detection
            results = pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                # testing exercie instructions
                v1 = v2 = v3 = 0
                current_instruction_v1_index = current_instruction_v2_index = current_instruction_v3_index = 0
                current_set = set()
                current_list = [] #will be translated to set when drawing connections
                total_num_of_exercise_instructions_in_stage = 0
                successful_exercise_instructions_in_current_stage = 0

                for exercise_instruction_loop in exerciseInstructions:
                    # we are checking only instructions that match the current stage
                    if exercise_instruction_loop.instructionStage != current_stage and exercise_instruction_loop.instructionStage != 0:
                        continue

                    # get current instruction
                    current_instruction = instructions[exercise_instruction_loop.instructionId - 1]

                    # test for Depth - only XY plain will be tested
                    if E_InstructionAxis[current_instruction.instructionAxis].value != E_InstructionAxis.XY.value:
                       continue

                    # count exercise instructions
                    if exercise_instruction_loop.instructionStage != 0:
                        total_num_of_exercise_instructions_in_stage += 1

                    current_instruction_v1_index = mp_pose.PoseLandmark[current_instruction.vertex1].value
                    current_instruction_v2_index = mp_pose.PoseLandmark[current_instruction.vertex2].value
                    current_instruction_v3_index = mp_pose.PoseLandmark[current_instruction.vertex3].value
                    v1 = [landmarks[current_instruction_v1_index].x,
                          landmarks[current_instruction_v1_index].y,
                          landmarks[current_instruction_v1_index].z]  # vertex 1 value
                    v2 = [landmarks[current_instruction_v2_index].x,
                          landmarks[current_instruction_v2_index].y,
                          landmarks[current_instruction_v2_index].z]  # vertex 2 value
                    v3 = [landmarks[current_instruction_v3_index].x,
                          landmarks[current_instruction_v3_index].y,
                          landmarks[current_instruction_v3_index].z]  # vertex 3 value

                    starting_angle = current_instruction.angle  # starting angle value
                    tested_angle = calculate_angle(v1, v2, v3,E_InstructionAxis[current_instruction.instructionAxis].value)  # calculating the current angle
                    #current_set.append([(mp_pose.PoseLandmark[current_instruction.vertex1].value,mp_pose.PoseLandmark[current_instruction.vertex2].value),
                     #                   (mp_pose.PoseLandmark[current_instruction.vertex2].value,mp_pose.PoseLandmark[current_instruction.vertex3].value)])
                    # searching for matching deviation trigger

                    if E_AlertDeviationTrigger[exercise_instruction_loop.alertDeviationTrigger].value == E_AlertDeviationTrigger.POSITIVE.value:
                        if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle:
                            print(current_instruction.insAlertData.alerttext)
                            current_list.append((current_instruction_v1_index, current_instruction_v2_index))
                            current_list.append((current_instruction_v2_index, current_instruction_v3_index))

                            '''mp_drawing.draw_landmarks(image, results.pose_landmarks, current_set,
                                                      mp_drawing.DrawingSpec(color=(0, 117, 66), thickness=2,
                                                                             circle_radius=2),  # vertex color
                                                      mp_drawing.DrawingSpec(color=(0, 66, 230), thickness=2,
                                                                             circle_radius=2)  # edges color
                                                      )'''
                            #print(
                            #    f'Positive Deviation found, exercise instruction {exercise_instruction_loop.exerciseInstructionId}')
                        #  print(f'Angle is {tested_angle}')
                        if starting_angle + exercise_instruction_loop.deviationNegative >= tested_angle:
                            successful_exercise_instructions_in_current_stage += 1
                        else:
                            """   print(f"Not enough motion range - Positive, instruction {exercise_instruction_loop.exerciseInstructionId}"
                                  f" Calculation is {starting_angle + exercise_instruction_loop.deviationNegative}"
                                  f" Tested angle is {tested_angle}")"""
                        continue
                    elif E_AlertDeviationTrigger[exercise_instruction_loop.alertDeviationTrigger].value == E_AlertDeviationTrigger.NEGATIVE.value:
                        if tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                            print(current_instruction.insAlertData.alerttext)
                            current_list.append((current_instruction_v1_index, current_instruction_v2_index))
                            current_list.append((current_instruction_v2_index, current_instruction_v3_index))

                            '''mp_drawing.draw_landmarks(image, results.pose_landmarks, current_set,
                                                      mp_drawing.DrawingSpec(color=(0, 117, 66), thickness=2,
                                                                             circle_radius=2),  # vertex color
                                                      mp_drawing.DrawingSpec(color=(0, 66, 230), thickness=2,
                                                                             circle_radius=2)  # edges color
                                                      )'''
                            #print(
                                #f'Negative Deviation found, exercise instruction {exercise_instruction_loop.exerciseInstructionId}')
                        #   print(f'Angle is {tested_angle}')
                        if starting_angle + exercise_instruction_loop.deviationPositive <= tested_angle:
                            successful_exercise_instructions_in_current_stage += 1
                        else:
                            """ print(f"Not enough motion range - Negative, instruction {exercise_instruction_loop.exerciseInstructionId}"
                                  f" Calculation is {starting_angle + exercise_instruction_loop.deviationPositive}"
                                  f" Tested angle is {tested_angle}")"""
                        continue

                    elif E_AlertDeviationTrigger[exercise_instruction_loop.alertDeviationTrigger].value == E_AlertDeviationTrigger.BOTH.value:
                        if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle or \
                                tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                            print(current_instruction.insAlertData.alerttext)
                            current_list.append((current_instruction_v1_index, current_instruction_v2_index))
                            current_list.append((current_instruction_v2_index, current_instruction_v3_index))

                            '''mp_drawing.draw_landmarks(image, results.pose_landmarks, current_set,
                                                      mp_drawing.DrawingSpec(color=(0, 117, 66), thickness=2,
                                                                             circle_radius=2),  # vertex color
                                                      mp_drawing.DrawingSpec(color=(0, 66, 230), thickness=2,
                                                                             circle_radius=2)  # edges color
                                                      )'''
                            #print(
                                #f'Deviation found, exercise instruction {exercise_instruction_loop.exerciseInstructionId}')
                        #  print(f'Angle is {tested_angle}')
                        continue

                if successful_exercise_instructions_in_current_stage == total_num_of_exercise_instructions_in_stage:
                    current_stage += rep_direction
                    # current_stage+=1

                if current_stage == exercise_stages:
                    # current_stage -= 1
                    if rep_direction == 1:
                        counter += 1
                    rep_direction = -1

                elif current_stage == 1:
                    rep_direction = 1
                    # current_stage = 1

                '''first = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y,
                         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].z]
                second = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z]
                third = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z]
                # Calculate angle
                angle = calculate_angle(first, second, third, E_InstructionAxis.XZ.value)
                second = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]'''

                # print(f' Right elbow z value: {landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x}')
                # print(f' Right shoulder z value: {landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x} \n')
                # to_visualize = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                # Visualize angle
                ''' cv2.putText(image, str(angle),
                            tuple(np.multiply(second, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA
                            )'''

                # Curl counter logic
            # if angle > 160:
            #  stage = "down"
            # if angle < 30 and stage == 'down':
            #    stage = "up"
            #   counter += 1
            #    print(counter)

            except:
                pass

            status_image = np.zeros((512, 256, 3), np.uint8)

            cv2.rectangle(status_image, (0, 0), (225, 73), (245, 117, 16), -1)

            # Rep data
            cv2.putText(status_image, 'REPS', (15, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(status_image, str(counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            # Stage data
            cv2.putText(status_image, 'STAGE', (65, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(status_image, str(current_stage),
                        (60, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.putText(status_image, 'STATE', (115, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(status_image, str(rep_direction),
                        (110, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.putText(status_image, "Alerts", (15, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)








            # Render detections
            '''new_set = mp_pose.POSE_CONNECTIONS
            new_set2 = new_set.difference(current_set)
            mp_drawing.draw_landmarks(image, results.pose_landmarks, new_set2,
                                      mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),  #vertex color
                                      mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)  #edges color
                                      )'''
            #results.pose_landmarks
            test_set = set()

            mp_drawing.draw_landmarks(image, results.pose_landmarks, set(current_list),
                                      mp_drawing.DrawingSpec(color=(0, 117, 66), thickness=0,
                                                             circle_radius=0),  # vertex color
                                      mp_drawing.DrawingSpec(color=(0, 66, 230), thickness=2,
                                                             circle_radius=2)  # edges color
                                      )

            image = cv2.resize(image, (512, 512))  # Resize image
            verti = np.concatenate((status_image,image),axis=1)
            cv2.imshow("testing",verti)


            #imS = cv2.resize(image, (1024, 768))  # Resize image
            #cv2.imshow('Mediapipe Feed', imS)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


print("Hello world")
my_est()
