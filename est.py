import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
from enum import Enum
import DBConnection

#if __name__ == '__main__':
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
                 alertDeviationTrigger, alertExtendedId) -> None:
        self.exerciseInstructionId = exerciseInstructionId
        self.exerciseId = exerciseId
        self.instructionId = instructionId
        self.alertId = alertId
        self.deviationPositive = deviationPositive
        self.deviationNegative = deviationNegative
        self.instructionStage = instructionStage
        self.exerciseInstructionType = exerciseInstructionType
        self.alertDeviationTrigger = alertDeviationTrigger
        self.alertExtendedId = alertExtendedId


class Instruction:
    def __init__(self, instructionId, vertex1, vertex2, vertex3, angle, description, instructionAxis) -> None:
        self.instructionId = instructionId
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.vertex3 = vertex3
        self.angle = angle
        self.description = description
        self.instructionAxis = instructionAxis
        self.instructionAlertData = None  # Alert Object


class Alerts:
    def __init__(self, alertId, alertInstructionId, alertText) -> None:
        self.alertId = alertId
        self.alertInstructionId = alertInstructionId
        self.alertText = alertText

# weshould find solution for all above my_est func

# Dummy exercise data:
exerciseId = 1
repsGoal = 10

# extracting exercise instruction data from db:
res = DBConnection.getAllExerciseInstructionData(exerciseId)
exerciseInstructionId, instructionId1, exerciseInstructionAlertId, deviationPositive, deviationNegative, instructionStage, exerciseInstructionType, \
alertDeviationTrigger, alertExtendedId = zip(*res)

res = DBConnection.getAllExerciseStages(exerciseId)
exercise_stages = res[0][0]

# QUERY 3: getting all instruction's data of the exercise
res = DBConnection.getAllInstructionData(exerciseId)
instructionId, vertex1, vertex2, vertex3, angle, description, instructionAxis = zip(*res)  # instruction's columns

# QUERY 4: getting all alert's data of the exercise
res = DBConnection.getAllAlertsData(exerciseId)
alertId2, alertInstructionId, alertText = zip(*res)

instructions_list = []
exerciseInstructions_list = []
instruction_alert_data_list = []

# creating alerts objects
for alert_Id, alert_instructionId, alert_Text in zip(alertId2, alertInstructionId, alertText):
    instruction_alert_data_list.append(Alerts(alert_Id, alert_instructionId, alert_Text))

# creating instructions and exerciseInstructions objects
for instruction_Id, v1, v2, v3, ang, instruction_desc, axis in zip(instructionId, vertex1, vertex2, vertex3, angle,
                                                                   description, instructionAxis):
    instructions_list.append(Instruction(instruction_Id, v1, v2, v3, ang, instruction_desc, axis))

# creating the relevant instructions
for item in instruction_alert_data_list:
    instructions_list[item.alertInstructionId - 1].instructionAlertData = item

# creating the relevant exercise instructions
for exerciseInstruction_Id, instruction_Id, alert_Id, deviation_Positive, deviation_Negative, instruction_Stage, exerciseInstruction_Type \
        , alertDeviation_Trigger, alertExtended_Id in zip(exerciseInstructionId, instructionId,
                                                          exerciseInstructionAlertId, deviationPositive,
                                                          deviationNegative,
                                                          instructionStage, exerciseInstructionType,
                                                          alertDeviationTrigger, alertExtendedId):
    exerciseInstructions_list.append(
        ExerciseInstruction(exerciseInstruction_Id, exerciseId, instruction_Id, alert_Id, deviation_Positive,
                            deviation_Negative, instruction_Stage, exerciseInstruction_Type, alertDeviation_Trigger,
                            alertExtended_Id))
    # end of dummy data


def my_est(e_id, r_num):
    # current stage variable
    current_stage = 0
    a = e_id
    b = r_num
    print(f"this is e_id {a} and this is r_num{b}")

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

    # cap = video that is captured through the web camera
    cap = cv2.VideoCapture(0)

    # the duration (in seconds) that the use will have to adjust him self
    duration = 2

    ret, frame = cap.read()
    start_time = datetime.now()
    diff = (datetime.now() - start_time).seconds  # converting into seconds
    while (diff <= duration):
        ret, frame = cap.read()
        imageResized = cv2.resize(frame, (1024, 768))  # Resize image
        cv2.putText(frame, str(diff), (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                    cv2.LINE_AA)  # adding timer text
        cv2.imshow('frame', imageResized)
        diff = (datetime.now() - start_time).seconds
        pressed_key = cv2.waitKey(10)

    cap.release()
    cv2.destroyAllWindows()

    cap = cv2.VideoCapture(0)

    # Exercise counter variables
    repetition_counter = 0
    stage = None
    repetition_direction = 1
    # Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.9, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            error_edges = []  # will be translated to set when drawing connections
            alerts_array = []  # contains all alerts that showed during the frame analysis
            # Make detection
            results = pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                # testing exercise instructions
                error_edges = []  # will be translated to set when drawing connections
                total_num_of_exercise_instructions_in_stage = 0
                successful_exercise_instructions_in_current_stage = 0

                for exercise_instruction_loop in exerciseInstructions_list:
                    # we are checking only instructions that match the current stage
                    if exercise_instruction_loop.instructionStage != current_stage and exercise_instruction_loop.instructionStage != 0:
                        continue

                    # get current instruction
                    current_instruction = instructions_list[exercise_instruction_loop.instructionId - 1]

                    # test for Depth - only XY plain will be tested
                    if E_InstructionAxis[current_instruction.instructionAxis].value != E_InstructionAxis.XY.value:
                        continue

                    # count exercise instructions
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
                    tested_angle = calculate_angle(v1, v2, v3, E_InstructionAxis[
                        current_instruction.instructionAxis].value)  # calculating the current angle

                    deviation_trigger_value = E_AlertDeviationTrigger[
                        exercise_instruction_loop.alertDeviationTrigger].value

                    if deviation_trigger_value == E_AlertDeviationTrigger.POSITIVE.value:
                        # check for deviation trigger
                        if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle:
                            alerts_array.append(current_instruction.instructionAlertData.alertText)
                            error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                            error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                        # check for extended deviation
                        if starting_angle + exercise_instruction_loop.deviationNegative >= tested_angle:
                            if starting_angle + exercise_instruction_loop.deviationNegative + exercise_instruction_loop.deviationPositive * -1 >= tested_angle:
                                alerts_array.append(
                                    instruction_alert_data_list[
                                        exercise_instruction_loop.alertExtendedId].alertText)
                                error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                                error_edges.append((current_instruction_v2_index, current_instruction_v3_index))
                            else:
                                successful_exercise_instructions_in_current_stage += 1
                        continue
                    elif deviation_trigger_value == E_AlertDeviationTrigger.NEGATIVE.value:
                        if tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                            alerts_array.append(current_instruction.instructionAlertData.alertText)
                            error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                            error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                        if starting_angle + exercise_instruction_loop.deviationPositive <= tested_angle:
                            if starting_angle + exercise_instruction_loop.deviationPositive + exercise_instruction_loop.deviationNegative * -1 <= tested_angle:
                                alerts_array.append(
                                    instruction_alert_data_list[
                                        exercise_instruction_loop.alertExtendedId].alertText)
                                error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                                error_edges.append((current_instruction_v2_index, current_instruction_v3_index))
                            else:
                                successful_exercise_instructions_in_current_stage += 1
                        continue

                    elif deviation_trigger_value == E_AlertDeviationTrigger.BOTH.value:
                        if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle or \
                                tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                            alerts_array.append(current_instruction.instructionAlertData.alertText)
                            error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                            error_edges.append((current_instruction_v2_index, current_instruction_v3_index))
                        else:
                            successful_exercise_instructions_in_current_stage += 1
                        continue

                if successful_exercise_instructions_in_current_stage == total_num_of_exercise_instructions_in_stage:
                    current_stage += repetition_direction

                if current_stage == exercise_stages:
                    if repetition_direction == 1:
                        repetition_counter += 1
                    repetition_direction = -1

                elif current_stage == 1:
                    repetition_direction = 1

            except:
                pass

            status_image = np.zeros((512, 720, 3), np.uint8)
            cv2.rectangle(status_image, (0, 0), (225, 73), (245, 117, 16), -1)

            # Rep data
            cv2.putText(status_image, 'REPS', (15, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(status_image, str(repetition_counter),
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
            cv2.putText(status_image, str(repetition_direction),
                        (110, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.putText(status_image, "Alerts:", (8, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                        cv2.LINE_AA)
            for item in alerts_array:
                cv2.putText(status_image, item, (8, 120 + alerts_array.index(item) * 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 0, 255), 1,
                            cv2.LINE_AA)

            # for green alert message if everything is okay
            if len(alerts_array) == 0:
                cv2.putText(status_image, "Keep The Good work!", (8, 120 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1,
                            cv2.LINE_AA)

            # draw error landmarks
            mp_drawing.draw_landmarks(image, results.pose_landmarks, set(error_edges),
                                      mp_drawing.DrawingSpec(color=(0, 117, 66), thickness=0,
                                                             circle_radius=0),  # vertex color
                                      mp_drawing.DrawingSpec(color=(0, 66, 230), thickness=2,
                                                             circle_radius=2)  # edges color
                                      )

            image = cv2.resize(image, (720, 512))  # Resize image
            verticalConcatenatedImage = np.concatenate((status_image, image), axis=1)

            cv2.imshow("AutomaticGymTrainer Feed", verticalConcatenatedImage)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

#my_est(1,2)
