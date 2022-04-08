from datetime import datetime

import mediapipe as mp
from PyQt5.QtCore import *
# for PyQT worker threads
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

from ClassObjects.Alerts import Alerts
from ClassObjects.EnumClasses import *
from ClassObjects.ExerciseInstruction import ExerciseInstruction
from ClassObjects.Instruction import Instruction
from ClassObjects.TriggeredAlerts import TriggeredAlerts
from Utils import DBConnection
from Utils.WorkoutEstimationFunctions import *
from cv2 import cv2

# Constants
NUMBER_OF_FRAMES_BETWEEN_SCORE = 15  # Ofir
SET_UP_DELAY_TIME = 0
IMAGE_WIDTH = 400
IMAGE_HEIGHT = 400


# QWidget
class EstimationScreen(QMainWindow):
    def __init__(self, exercise_id, repetition_num):
        super(EstimationScreen, self).__init__()
        loadUi("./ui/workoutfeed.ui", self)

        self.setFixedSize(1000, 900)

        '''
        self.VBL = QVBoxLayout()
        '''

        # camera feed
        '''
        self.CameraImageFeedLabel = QLabel()
        self.VBL.addWidget(self.CameraImageFeedLabel)
        

        # Goal Image feed
        self.GoalImageFeedLabel = QLabel()
        self.VBL.addWidget(self.GoalImageFeedLabel)

        # Wrong posture image feed
        self.WrongPostureImageFeedLabel = QLabel()
        self.VBL.addWidget(self.WrongPostureImageFeedLabel)
        '''

        self.CameraImageFeedLabel = None
        self.GoalImageFeedLabel = None
        self.WrongPostureImageFeedLabel = None

        # Set thread
        self.WorkoutEstimation = WorkoutEstimation(exercise_id=exercise_id, repetition_num=repetition_num)
        self.WorkoutEstimation.start()

        # For camera feed
        self.WorkoutEstimation.CameraImageUpdate.connect(self.CameraImageUpdateSlot)
        # For goal image feed
        self.WorkoutEstimation.GoalImageUpdate.connect(self.GoalImageUpdateSlot)
        # For wrong posture feed
        self.WorkoutEstimation.WrongPostureImageUpdate.connect(self.WrongPostureImageUpdateSlot)

        # self.setLayout(self.VBL)

        # Set Rep Goal label
        self.lbl_repGoalValue.setText(str(repetition_num))
        self.lbl_repCurrentValue.setText('0')
        self.WorkoutEstimation.RepetitionCounterUpdate.connect(self.UpdateRepetitionLabel)

    def CameraImageUpdateSlot(self, Image):
        self.lbl_webcamImage.setPixmap(QPixmap.fromImage(Image))
        # self.CameraImageFeedLabel.setPixmap(QPixmap.fromImage(Image))

    def GoalImageUpdateSlot(self, Image):
        self.lbl_goalImage.setPixmap(QPixmap.fromImage(Image))
        # self.GoalImageFeedLabel.setPixmap(QPixmap.fromImage(Image))

    def WrongPostureImageUpdateSlot(self, Image):
        self.lbl_errorImage.setPixmap(QPixmap.fromImage(Image))
        # self.WrongPostureImageFeedLabel.setPixmap(QPixmap.fromImage(Image))

    def UpdateRepetitionLabel(self, rep_counter):
        self.lbl_repCurrentValue.setText(str(rep_counter))


class WorkoutEstimation(QThread):
    CameraImageUpdate = pyqtSignal(QImage)  # For trainee camera
    GoalImageUpdate = pyqtSignal(QImage)  # For trainee goal posture
    WrongPostureImageUpdate = pyqtSignal(QImage)  # For trainee wrong posture
    RepetitionCounterUpdate = pyqtSignal(int)  # For repetition update

    def __init__(self, exercise_id, repetition_num, parent=None):
        QThread.__init__(self, parent)
        self.exercise_id = exercise_id
        self.repetition_num = repetition_num

    def run(self):  # estimation // my_est
        self.ThreadActive = True

        '''
        1 - Before starting the exercise we fetch every relevant detail from the DB. 
        2 - We create relevant objects such as instructions, alerts and exercise instructions.
        '''
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose

        # extracting exercise instruction data from db:
        res = DBConnection.getAllExerciseInstructionData(self.exercise_id)
        exerciseInstructionId, instructionId1, exerciseInstructionAlertId, deviationPositive, deviationNegative, \
        instructionStage, exerciseInstructionType, alertDeviationTrigger, alertExtendedId = zip(*res)

        res = DBConnection.getAllExerciseStages(self.exercise_id)
        exercise_stages = res[0][0]

        # QUERY 3: getting all instruction's data of the exercise
        res = DBConnection.getAllInstructionData(self.exercise_id)
        instructionId, vertex1, vertex2, vertex3, angle, description, instructionAxis = zip(
            *res)  # instruction's columns

        # QUERY 4: getting all alert's data of the exercise
        res = DBConnection.getAllAlertsData(self.exercise_id)
        alertId2, alertInstructionId, alertText, alert_wrong_posture_image_link = zip(*res)

        # QUERY 8: get all images for specific exercise
        all_stage_images_links = DBConnection.getExerciseImages(self.exercise_id)

        instructions_list = []
        exercise_instructions_list = []
        instruction_alert_data_list = []

        # creating alerts objects
        for alert_Id, alert_instructionId, alert_Text, wrong_posture_links in zip(alertId2, alertInstructionId,
                                                                                  alertText,
                                                                                  alert_wrong_posture_image_link):
            instruction_alert_data_list.append(Alerts(alert_Id, alert_instructionId, alert_Text, wrong_posture_links))

        # creating instructions and exerciseInstructions objects
        for instruction_Id, vertex1_coordinates, vertex2_coordinates, vertex3_coordinates, ang, instruction_desc, axis in zip(
                instructionId, vertex1, vertex2, vertex3,
                angle,
                description, instructionAxis):
            instructions_list.append(
                Instruction(instruction_Id, vertex1_coordinates, vertex2_coordinates, vertex3_coordinates, ang,
                            instruction_desc, axis))

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
            exercise_instructions_list.append(
                ExerciseInstruction(exerciseInstruction_Id, self.exercise_id, instruction_Id, alert_Id,
                                    deviation_Positive,
                                    deviation_Negative, instruction_Stage, exerciseInstruction_Type,
                                    alertDeviation_Trigger,
                                    alertExtended_Id))

        # Ofir
        # convert all links to actual images
        stage_images = []  # change stage images to exercise images
        for image_links in all_stage_images_links:  # all_stage_images_links contains tuples
            stage_images.append(getImageFromLink(image_links[0]))

        # Ofir
        # Get all alert images
        alert_wrong_images = []
        for alert in instruction_alert_data_list:
            alert_wrong_images.append(getImageFromLink(alert.alert_wrong_posture_image_link))

        # current stage variable
        current_stage = 0  # current stage
        exercise_score = 100  # exercise score
        exercise_score_frame_counter = 0  # each NUMBER_OF_FRAMES_BETWEEN_SCORE frames we calculate the score
        wrong_posture_image_to_display = getImageFromLink('https://i.imgur.com/9Prp4Da.jpg')
        error_list = []  # contains list triggeredAlerts
        update_posture_image_flag = False
        update_goal_image_flag = False

        # cap = video that is captured through the web camera
        cap = cv2.VideoCapture(0)

        ret, frame = cap.read()
        start_time = datetime.now()
        diff = (datetime.now() - start_time).seconds  # converting into seconds
        while diff <= SET_UP_DELAY_TIME:
            ret, frame = cap.read()
            camera_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.putText(frame, str(diff), (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                        cv2.LINE_AA)  # adding timer text

            ConvertToQtFormat = QImage(camera_image.data, camera_image.shape[1], camera_image.shape[0],
                                       QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(IMAGE_WIDTH, IMAGE_HEIGHT, Qt.KeepAspectRatio)
            self.CameraImageUpdate.emit(Pic)
            diff = (datetime.now() - start_time).seconds

        cap.release()
        cv2.destroyAllWindows()

        # End of trainee setup #

        # start estimation
        cap = cv2.VideoCapture(0)

        # Exercise counter variables
        repetition_counter = 0
        stage = None
        repetition_direction = 1
        # Setup mediapipe instance
        with mp_pose.Pose(min_detection_confidence=0.9, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                # Reset Image flags
                update_posture_image_flag = False
                update_goal_image_flag = False

                # Read webcam image
                ret, frame = cap.read()
                # counting that a frame was received
                exercise_score_frame_counter += 1

                # Change this line later on - instead of link grab it from somewhere

                camera_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                camera_image.flags.writeable = False

                error_edges = []  # will be translated to set when drawing connections
                alerts_array = []  # contains all alerts that showed during the frame analysis
                # Make detection
                results = pose.process(camera_image)

                # Recolor back to BGR
                camera_image.flags.writeable = True
                camera_image = cv2.cvtColor(camera_image, cv2.COLOR_RGB2BGR)

                # Extract landmarks
                try:
                    landmarks = results.pose_landmarks.landmark

                    # testing exercise instructions
                    error_edges = []  # will be translated to set when drawing connections
                    total_num_of_exercise_instructions_in_stage = 0
                    successful_exercise_instructions_in_current_stage = 0

                    for exercise_instruction_loop in exercise_instructions_list:
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
                        vertex1_coordinates = [landmarks[current_instruction_v1_index].x,
                                               landmarks[current_instruction_v1_index].y,
                                               landmarks[current_instruction_v1_index].z]  # vertex 1 value
                        vertex2_coordinates = [landmarks[current_instruction_v2_index].x,
                                               landmarks[current_instruction_v2_index].y,
                                               landmarks[current_instruction_v2_index].z]  # vertex 2 value
                        vertex3_coordinates = [landmarks[current_instruction_v3_index].x,
                                               landmarks[current_instruction_v3_index].y,
                                               landmarks[current_instruction_v3_index].z]  # vertex 3 value

                        starting_angle = current_instruction.angle  # starting angle value
                        tested_angle = calculateAngle(vertex1_coordinates, vertex2_coordinates, vertex3_coordinates,
                                                      E_InstructionAxis[
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
                                wrong_posture_image_to_display = alert_wrong_images[
                                    exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0
                                update_posture_image_flag = True

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
                                    wrong_posture_image_to_display = alert_wrong_images[
                                        exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0
                                    update_posture_image_flag = True

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
                                wrong_posture_image_to_display = alert_wrong_images[
                                    exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0
                                update_posture_image_flag = True

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
                                    wrong_posture_image_to_display = alert_wrong_images[
                                        exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0
                                    update_posture_image_flag = True

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
                                wrong_posture_image_to_display = alert_wrong_images[
                                    exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0
                                update_posture_image_flag = True

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
                        update_goal_image_flag = True

                    if current_stage == exercise_stages:
                        if repetition_direction == 1:
                            repetition_counter += 1
                            self.RepetitionCounterUpdate.emit(repetition_counter)
                        repetition_direction = -1

                    elif current_stage == 1:
                        repetition_direction = 1

                except Exception as e:
                    print(e)
                    # status image alerts
                '''status_image = np.zeros((512, 720, 3), np.uint8)
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
                                '''

                # draw error landmarks
                mp_drawing.draw_landmarks(camera_image, results.pose_landmarks, set(error_edges),
                                          mp_drawing.DrawingSpec(color=(0, 117, 66), thickness=0,
                                                                 circle_radius=0),  # vertex color
                                          mp_drawing.DrawingSpec(color=(0, 66, 230), thickness=2,
                                                                 circle_radius=2)  # edges color
                                          )

                # Recolor camera image
                camera_image = cv2.cvtColor(camera_image, cv2.COLOR_BGR2RGB)
                # Resize image
                camera_image = cv2.resize(camera_image,
                                          (IMAGE_WIDTH, IMAGE_HEIGHT))

                # Camera image update
                ConvertToQtFormat = QImage(camera_image.data, camera_image.shape[1],
                                           camera_image.shape[0], QImage.Format_RGB888)
                # CameraImagePic = ConvertToQtFormat.scaled(600, 600, Qt.KeepAspectRatio)
                self.CameraImageUpdate.emit(ConvertToQtFormat)

                if update_goal_image_flag:
                    # Goal Posture image update
                    goal_pose_image = stage_images[current_stage + repetition_direction - 1]
                    goal_pose_image = cv2.cvtColor(goal_pose_image, cv2.COLOR_BGR2RGB)
                    # Resize image
                    goal_pose_image = cv2.resize(goal_pose_image, (IMAGE_WIDTH, IMAGE_HEIGHT))

                    # Goal image update
                    ConvertToQtFormat = QImage(goal_pose_image.data, goal_pose_image.shape[1],
                                               goal_pose_image.shape[0], QImage.Format_RGB888)
                    # GoalImagePic = ConvertToQtFormat.scaled(IMAGE_WIDTH, IMAGE_HEIGHT, Qt.KeepAspectRatio)
                    self.GoalImageUpdate.emit(ConvertToQtFormat)

                if update_posture_image_flag:
                    # Wrong posture image update
                    wrong_posture_image_to_display = cv2.cvtColor(wrong_posture_image_to_display, cv2.COLOR_BGR2RGB)
                    # Resize image
                    wrong_posture_image_to_display = cv2.resize(wrong_posture_image_to_display,
                                                                (IMAGE_WIDTH, IMAGE_HEIGHT))

                    # Wrong posture image update
                    ConvertToQtFormat = QImage(wrong_posture_image_to_display.data,
                                               wrong_posture_image_to_display.shape[1],
                                               wrong_posture_image_to_display.shape[0], QImage.Format_RGB888)
                    # WrongImagePic = ConvertToQtFormat.scaled(IMAGE_WIDTH, IMAGE_HEIGHT, Qt.KeepAspectRatio)
                    self.WrongPostureImageUpdate.emit(ConvertToQtFormat)

                try:
                    error_list = list(set(error_list))  # make sure there are no copies
                except Exception as e:
                    print(e)
                if repetition_counter == self.repetition_num:
                    self.score = exercise_score
                    # ToDo: set exercise logs as well in self.

            cap.release()
            cv2.destroyAllWindows()
            self.ThreadActive = False
            self.quit()

# my_est(1,5)


# ToDo:  '''
#  2.1  Update both DB (Alon & Ofir)
#  3.3  See how we move forward to next page after this page closes
#  3.4  Add default case if flag has do not changed for mistake image
#  4.   Update default image
#  5.   ''' Important - See how we change the alert so
#           we can just go through index (in the for loops in the start of the code)'''
#  '''

# ToDo: General
#   1. Add doc to each class to make sure it is understandable
#   2. Update requirements.txt (if needed)
#   3. Delete irreverent classes (such as est.py) - Only after pushing to git and making a valid version!
#   4. Keep rewriting code if needed
#   5. Update images if needed
#   6. ....
#  '''
