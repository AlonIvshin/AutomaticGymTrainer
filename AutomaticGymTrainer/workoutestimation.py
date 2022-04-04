import mediapipe as mp
from datetime import datetime
from Utils import DBConnection

from ClassObjects import Alerts, E_AlertDeviationTrigger, E_InstructionAxis, \
    ExerciseInstruction, Instruction, TriggeredAlerts


from Utils.WorkoutEstimationFunctions import *

"""class WorkoutEstimation(QMainWindow):
    def __init__(self):
        super(WorkoutEstimation, self).__init__()
        loadUi("./ui/workoutfeed.ui", self)
        self.setFixedSize(1200, 800)

        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        # Cancel button here #

        self.setLayout(self.VBL)


# Getting image from camera to a format PyQt can understand
class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        Capture



if __name__ == "main":
    App = QApplication(sys.argv)
    Root = WorkoutEstimation()
    Root.show()
    sys.exit(App.exit())
"""

# if __name__ == '__main__':
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
NUMBER_OF_FRAMES_BETWEEN_SCORE = 15  # Ofir
FIRST_CAMERA_DELAY_TIME = 2

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

# QUERY 8: get all images for specific exercise
all_stage_images_links = DBConnection.getExerciseImages(exerciseId)

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

# Ofir
# convert all links to actual images
stage_images = []  # change stage images to exercise images
for image_links in all_stage_images_links:  # all_stage_images_links contains tuples
    stage_images.append(getImageFromLink(image_links[0]))


def my_est(e_id, r_num):
    # current stage variable
    current_stage = 0  # current stage
    exercise_score = 100  # exercise score
    exercise_score_frame_counter = 0  # each NUMBER_OF_FRAMES_BETWEEN_SCORE frames we calculate the score

    error_list = []  # contains list triggeredAlerts
    a = e_id
    b = r_num
    print(f"this is e_id {a} and this is r_num {b}")

    # cap = video that is captured through the web camera
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()
    start_time = datetime.now()
    diff = (datetime.now() - start_time).seconds  # converting into seconds
    while (diff <= FIRST_CAMERA_DELAY_TIME):
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
            # counting that a frame was received
            exercise_score_frame_counter += 1
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
                    tested_angle = calculateAngle(v1, v2, v3, E_InstructionAxis[
                        current_instruction.instructionAxis].value)  # calculating the current angle

                    deviation_trigger_value = E_AlertDeviationTrigger[
                        exercise_instruction_loop.alertDeviationTrigger].value

                    if deviation_trigger_value == E_AlertDeviationTrigger.POSITIVE.value:
                        # check for deviation trigger
                        if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle:
                            alerts_array.append(current_instruction.instructionAlertData.alertText)
                            error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                            error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                            # Save alerts that triggered during the exercise
                            error_list.append(
                                TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                repNumber=repetition_counter))

                            # ofir - score
                            if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                exercise_score_frame_counter = 0
                                exercise_score -= calculateScore(
                                    tested_angle - exercise_instruction_loop.deviationPositive - starting_angle)

                        # check for extended deviation
                        if starting_angle + exercise_instruction_loop.deviationNegative >= tested_angle:
                            if starting_angle + exercise_instruction_loop.deviationNegative + exercise_instruction_loop.deviationPositive * -1 >= tested_angle:
                                alerts_array.append(
                                    instruction_alert_data_list[
                                        exercise_instruction_loop.alertExtendedId].alertText)
                                error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                                error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                                # Save alerts that triggered during the exercise
                                error_list.append(
                                    TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                    repNumber=repetition_counter))

                                # ofir - score
                                if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                    exercise_score_frame_counter = 0
                                    exercise_score -= calculateScore(
                                        starting_angle + exercise_instruction_loop.deviationNegative + exercise_instruction_loop.deviationPositive * -1 - tested_angle)
                            else:
                                successful_exercise_instructions_in_current_stage += 1
                        continue
                    elif deviation_trigger_value == E_AlertDeviationTrigger.NEGATIVE.value:
                        if tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                            alerts_array.append(current_instruction.instructionAlertData.alertText)
                            error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                            error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                            # Save alerts that triggered during the exercise
                            error_list.append(
                                TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                repNumber=repetition_counter))

                            # ofir - score
                            if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                exercise_score_frame_counter = 0
                                exercise_score -= calculateScore(
                                    starting_angle - tested_angle - exercise_instruction_loop.deviationNegative)

                        if starting_angle + exercise_instruction_loop.deviationPositive <= tested_angle:
                            if starting_angle + exercise_instruction_loop.deviationPositive + exercise_instruction_loop.deviationNegative * -1 <= tested_angle:
                                alerts_array.append(
                                    instruction_alert_data_list[
                                        exercise_instruction_loop.alertExtendedId].alertText)
                                error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                                error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                                # Save alerts that triggered during the exercise
                                error_list.append(
                                    TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                    repNumber=repetition_counter))

                                # ofir - score
                                if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                    exercise_score_frame_counter = 0
                                    exercise_score -= calculateScore(
                                        tested_angle - starting_angle + exercise_instruction_loop.deviationPositive + exercise_instruction_loop.deviationNegative * -1)
                            else:
                                successful_exercise_instructions_in_current_stage += 1
                        continue

                    elif deviation_trigger_value == E_AlertDeviationTrigger.BOTH.value:
                        if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle or \
                                tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                            alerts_array.append(current_instruction.instructionAlertData.alertText)
                            error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                            error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                            # Save alerts that triggered during the exercise
                            error_list.append(
                                TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                repNumber=repetition_counter))

                            # ofir - score
                            if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                exercise_score_frame_counter = 0
                                exercise_score -= calculateScore(
                                    max(tested_angle - exercise_instruction_loop.deviationPositive,
                                        tested_angle - exercise_instruction_loop.deviationNegative))

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

            # Ideal pose with camera feed concatenation - ofir
            goal_pose_image = stage_images[current_stage + repetition_direction - 1]
            cv2.putText(goal_pose_image, "Goal Posture:", (30, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                        cv2.LINE_AA)

            goal_pose_image = cv2.resize(goal_pose_image, (720, 512))  # Resize image
            image = cv2.resize(image, (720, 512))  # Resize image
            status_image = cv2.resize(status_image, (1440, 512))

            verticalConcatenatedImage = np.concatenate((goal_pose_image, image), axis=1)  # on x axis
            horizontalConcatenatedImage = np.concatenate((verticalConcatenatedImage, status_image), axis=0)

            # image = cv2.resize(image, (720, 512))  # Resize image
            # verticalConcatenatedImage = np.concatenate((status_image, image), axis=1)

            # Concatenation with ideal position for each stage - ofir

            cv2.imshow("AutomaticGymTrainer Feed", horizontalConcatenatedImage)

            error_list = list(set(error_list))  # make sure there are no copies

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

            if repetition_counter == r_num:
                break

        cap.release()
        cv2.destroyAllWindows()

        # Need to fix return
        # return exercise_score

# my_est(1,5)
