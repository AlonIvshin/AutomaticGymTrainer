import functools  # for custom comparator
import queue
import threading
from datetime import datetime

import mediapipe as mp
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, Qt
# for PyQT worker threads
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit
from cv2 import cv2

from ClassObjects.Alerts import Alerts
from ClassObjects.EnumClasses import *
from ClassObjects.ExerciseInstruction import ExerciseInstruction
from ClassObjects.Feedback import Feedback
from ClassObjects.FeedbackLog import FeedbackLog
from ClassObjects.Instruction import Instruction
from ClassObjects.TriggeredAlerts import TriggeredAlerts
from Utils import DBConnection
from Utils.WorkoutEstimationFunctions import *
from score import FeedbackScreen

# Constants
NUMBER_OF_FRAMES_BETWEEN_SCORE = 150  # Ofir
SET_UP_DELAY_TIME = 4
IMAGE_WIDTH = 400
IMAGE_HEIGHT = 400
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


# QWidget
class EstimationScreen(QMainWindow):
    def __init__(self, exercise_id, repetition_num, widget, user_id):
        super().__init__()
        self.ui = uic.loadUi("./ui/workoutfeed.ui", self)
        self.setFixedSize(1920, 1000)
        self.exercise_id = exercise_id
        self.repetition_num = repetition_num

        self.parameters_queue = None
        self.fetch_data_thread = None

        self.widget = widget
        self.user_id = user_id

        # Set thread
        # self.parameters_for_thread = list(self.SetUpExerciseData())
        self.parameters_queue = queue.Queue()
        self.fetch_data_thread = threading.Thread(target=self.SetUpExerciseData, args=[self.parameters_queue],
                                                  daemon=True)
        self.fetch_data_thread.daemon = True
        self.fetch_data_thread.start()

        self.WorkoutEstimation = WorkoutEstimationThread(repetition_num=self.repetition_num,
                                                         parameters_thread=self.fetch_data_thread,
                                                         parameters_queue=self.parameters_queue, estimation_screen=self,
                                                         widget=self.widget)

        # For camera feed
        self.WorkoutEstimation.CameraImageUpdate.connect(self.CameraImageUpdateSlot)
        '''# For goal image feed
        self.WorkoutEstimation.GoalImageUpdate.connect(self.GoalImageUpdateSlot)'''
        # For wrong posture feed
        self.WorkoutEstimation.PostureImageUpdate.connect(self.PostureImageUpdateSlot)

        # Set Rep Goal label
        self.lbl_repGoalValue.setText(str(repetition_num))
        self.lbl_repCurrentValue.setText('0')
        self.WorkoutEstimation.RepetitionCounterUpdate.connect(self.UpdateRepetitionLabel)

        # Move forward to next screen when trainee finished the exericse:
        self.WorkoutEstimation.ScoreScreenReadyUpdate.connect(self.ScoreScreenReadyUpdateSlot)

        # Set alerts for user to review
        self.WorkoutEstimation.TriggeredAlertsUpdate.connect(self.TriggeredAlertsUpdateSlot)

        self.WorkoutEstimation.daemon = True  # Not working
        self.WorkoutEstimation.start()

    def ScoreScreenReadyUpdateSlot(self, feedback_id):
        FeedbackScreen_holder = FeedbackScreen(feedback_id=str(feedback_id), widget=self.widget)
        self.widget.removeWidget(self.widget.currentWidget())
        # reloading app.py
        self.widget.currentWidget().loadMain(self.user_id)
        self.widget.currentWidget().loadDataHistory(self.user_id)
        self.widget.addWidget(FeedbackScreen_holder)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    def CameraImageUpdateSlot(self, Image):
        self.lbl_webcamImage.setPixmap(QPixmap.fromImage(Image))
        # self.CameraImageFeedLabel.setPixmap(QPixmap.fromImage(Image))

    '''def GoalImageUpdateSlot(self, Image):
        self.lbl_goalImage.setPixmap(QPixmap.fromImage(Image))
        # self.GoalImageFeedLabel.setPixmap(QPixmap.fromImage(Image))'''

    def PostureImageUpdateSlot(self, Image):
        self.lbl_postureImage.setPixmap(QPixmap.fromImage(Image))
        # self.WrongPostureImageFeedLabel.setPixmap(QPixmap.fromImage(Image))

    def UpdateRepetitionLabel(self, rep_counter):
        self.lbl_repCurrentValue.setText(str(rep_counter))

    def TriggeredAlertsUpdateSlot(self, triggered_alerts_for_last_rep):  # Receives an array that has all texts
        txt = ''
        for item in triggered_alerts_for_last_rep:
            txt += item + '\n'
        self.txt_TriggeredAlerts.clear()
        self.txt_TriggeredAlerts.insertPlainText(str(txt))

    def getUserId(self):
        return self.user_id

    def getExerciseId(self):
        return self.exercise_id

    def SetUpExerciseData(self, queue):
        # Get relevant data from DB:
        # extracting exercise instruction data from db:
        res = DBConnection.getAllExerciseInstructionData(self.exercise_id)
        exerciseInstructionId, instructionId1, exerciseInstructionAlertId, deviationPositive, deviationNegative, instructionStage, exerciseInstructionType, alertDeviationTrigger, alertExtendedId = zip(
            *res)

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
        all_stage_images_links = sorted(all_stage_images_links, key=lambda x: x[0])
        for index in range(len(all_stage_images_links)):
            all_stage_images_links[index] = all_stage_images_links[index][1]

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

        '''# creating the relevant instructions
        for item in instruction_alert_data_list:
            instructions_list[item.alertInstructionId - 1].instructionAlertData = item'''

        for item in instruction_alert_data_list:
            for index in range(len(instructions_list)):
                if instructions_list[index].instructionId == item.alertInstructionId:
                    instructions_list[index].instructionAlertData = item
                    break

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
            stage_images.append(getImageFromLink(image_links))

        # Ofir
        # Get all alert images
        '''alert_wrong_images = []
        for alert in instruction_alert_data_list:
            alert_wrong_images.append(getImageFromLink(alert.alert_wrong_posture_image_link))'''

        queue.put(exercise_instructions_list)
        queue.put(instructions_list)
        # queue.put(alert_wrong_images)
        queue.put(instruction_alert_data_list)
        queue.put(exercise_stages)
        queue.put(stage_images)

        '''queue.put(mp_pose, exercise_instructions_list, instructions_list, alert_wrong_images, instruction_alert_data_list,
                  exercise_stages, mp_drawing, stage_images)'''
        # return mp_pose, exercise_instructions_list, instructions_list, alert_wrong_images, instruction_alert_data_list, exercise_stages, mp_drawing, stage_images


class WorkoutEstimationThread(QThread):
    CameraImageUpdate = pyqtSignal(QImage)  # For trainee camera
    # GoalImageUpdate = pyqtSignal(QImage)           # For trainee goal posture
    PostureImageUpdate = pyqtSignal(QImage)  # For trainee wrong posture
    RepetitionCounterUpdate = pyqtSignal(int)  # For repetition update
    ScoreScreenReadyUpdate = pyqtSignal(object)  # For moving towards next screen, notifying the GUI thread
    TriggeredAlertsUpdate = pyqtSignal(object)  # For updating alerts in the GUI text box

    def __init__(self, repetition_num, parameters_queue, parameters_thread, estimation_screen, widget):
        QThread.__init__(self)
        self.repetition_num = int(repetition_num)
        self.parameters_queue = parameters_queue
        self.parameters_thread = parameters_thread
        self.score = 100
        self.estimation_screen = estimation_screen
        self.widget = widget

    def run(self):  # estimation // my_est
        # current stage variable
        '''mp_pose, exercise_instructions_list, instructions_list, alert_wrong_images, instruction_alert_data_list, exercise_stages, mp_drawing, stage_images = (
            self.parameters)
        '''
        current_stage = 0  # current stage
        exercise_score = 100  # exercise score
        exercise_score_frame_counter = 0  # each NUMBER_OF_FRAMES_BETWEEN_SCORE frames we calculate the score
        wrong_posture_image_to_display = getImageFromLink('https://i.imgur.com/9Prp4Da.jpg')
        triggered_error_list = []  # contains list triggeredAlerts

        # cap = video that is captured through the web camera
        cap = cv2.VideoCapture(0)

        ret, frame = cap.read()
        start_time = datetime.now()
        diff = (datetime.now() - start_time).seconds  # converting into seconds
        while diff <= SET_UP_DELAY_TIME:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            camera_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            figureImg = cv2.imread('etc./figure.png')
            camera_image = cv2.addWeighted(camera_image, 0.6, figureImg, 0.4, 0)
            cv2.putText(frame, str(diff), (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                        cv2.LINE_AA)  # adding timer text

            ConvertToQtFormat = QImage(camera_image.data, camera_image.shape[1], camera_image.shape[0],
                                       QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(IMAGE_WIDTH, IMAGE_HEIGHT, Qt.KeepAspectRatio)
            self.CameraImageUpdate.emit(Pic)
            diff = (datetime.now() - start_time).seconds

        # cap.release()
        # cv2.destroyAllWindows()

        # End of trainee setup #

        # Fetch data from thread and wait until all data has been fetched
        self.parameters_thread.join()
        # mp_pose = self.parameters_queue.get()
        exercise_instructions_list = self.parameters_queue.get()
        instructions_list = self.parameters_queue.get()
        # alert_wrong_images = self.parameters_queue.get()
        instruction_alert_data_list = self.parameters_queue.get()
        exercise_stages = self.parameters_queue.get()
        # mp_drawing = self.parameters_queue.get()
        stage_images = self.parameters_queue.get()
        print("data fetched")

        # start estimation
        # cap = cv2.VideoCapture(0)

        # Exercise counter variables
        repetition_counter = 0
        repetition_direction = 1

        # Setup mediapipe instance
        with mp_pose.Pose(min_detection_confidence=0.9, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                # Reset Image flags
                update_posture_image_flag = False
                # update_goal_image_flag = False

                # Read webcam image
                ret, frame = cap.read()

                # counting that a frame was received
                exercise_score_frame_counter += 1

                # Change this line later on - instead of link grab it from somewhere

                camera_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                camera_image.flags.writeable = False

                error_edges = []  # will be translated to set when drawing connections
                triggered_error_list_text = []  # contains all alerts that showed during the frame analysis
                # Make detection
                results = pose.process(camera_image)  ##########CRASH
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
                        for item in instructions_list:
                            if item.instructionId == exercise_instruction_loop.instructionId:
                                current_instruction = item
                                break
                        # current_instruction = instructions_list[exercise_instruction_loop.instructionId - 1]

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
                                                          current_instruction.instructionAxis].value)  # calculating
                        # the current angle

                        deviation_trigger_value = E_AlertDeviationTrigger[
                            exercise_instruction_loop.alertDeviationTrigger].value

                        if deviation_trigger_value == E_AlertDeviationTrigger.POSITIVE.value:
                            # check for deviation trigger
                            if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle:
                                triggered_error_list_text.append(current_instruction.instructionAlertData.alertText)
                                error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                                error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                                triggered_alert_to_add = TriggeredAlerts(exercise_instruction_loop.alertId,
                                                                         stageNumber=current_stage,
                                                                         repNumber=repetition_counter)
                                triggered_alert_exist_flag = False
                                for item in triggered_error_list:
                                    if triggered_alert_to_add.alertId == item.alertId and \
                                            triggered_alert_to_add.repNumber == item.repNumber and \
                                            triggered_alert_to_add.stageNumber == item.stageNumber:
                                        triggered_alert_exist_flag = True
                                if not triggered_alert_exist_flag:
                                    triggered_error_list.append(triggered_alert_to_add)
                                    exercise_score -= calculateScore(
                                        tested_angle - exercise_instruction_loop.deviationPositive - starting_angle)

                                """# Save alerts that triggered during the exercise
                                triggered_error_list.append(
                                    TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                    repNumber=repetition_counter))
                                '''wrong_posture_image_to_display = alert_wrong_images[
                                    exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0'''
                                update_posture_image_flag = True

                                # ofir - score
                                if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                    exercise_score_frame_counter = 0
                                    exercise_score -= calculateScore(
                                        tested_angle - exercise_instruction_loop.deviationPositive - starting_angle)"""

                            # check for extended deviation
                            if starting_angle + exercise_instruction_loop.deviationNegative >= tested_angle:
                                if starting_angle + exercise_instruction_loop.deviationNegative + exercise_instruction_loop.deviationPositive * -1 >= tested_angle:
                                    for item in instruction_alert_data_list:
                                        if item.alertId == exercise_instruction_loop.alertExtendedId:
                                            triggered_error_list_text.append(item.alertText)
                                            break

                                    '''triggered_error_list_text.append(
                                        instruction_alert_data_list[
                                            exercise_instruction_loop.alertExtendedId].alertText)'''
                                    error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                                    error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                                    triggered_alert_to_add = TriggeredAlerts(exercise_instruction_loop.alertId,
                                                                             stageNumber=current_stage,
                                                                             repNumber=repetition_counter)
                                    triggered_alert_exist_flag = False
                                    for item in triggered_error_list:
                                        if triggered_alert_to_add.alertId == item.alertId and \
                                                triggered_alert_to_add.repNumber == item.repNumber and \
                                                triggered_alert_to_add.stageNumber == item.stageNumber:
                                            triggered_alert_exist_flag = True
                                    if not triggered_alert_exist_flag:
                                        triggered_error_list.append(triggered_alert_to_add)
                                        exercise_score -= calculateScore(
                                            starting_angle + exercise_instruction_loop.deviationNegative + exercise_instruction_loop.deviationPositive * -1 - tested_angle)

                                    """# Save alerts that triggered during the exercise
                                    triggered_error_list.append(
                                        TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                        repNumber=repetition_counter))
                                    '''wrong_posture_image_to_display = alert_wrong_images[
                                        exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0'''
                                    update_posture_image_flag = True

                                    # ofir - score
                                    if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                        exercise_score_frame_counter = 0
                                        exercise_score -= calculateScore(
                                            starting_angle + exercise_instruction_loop.deviationNegative + exercise_instruction_loop.deviationPositive * -1 - tested_angle)"""
                                else:
                                    successful_exercise_instructions_in_current_stage += 1
                            continue
                        elif deviation_trigger_value == E_AlertDeviationTrigger.NEGATIVE.value:
                            if tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                                triggered_error_list_text.append(current_instruction.instructionAlertData.alertText)
                                error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                                error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                                triggered_alert_to_add = TriggeredAlerts(exercise_instruction_loop.alertId,
                                                                         stageNumber=current_stage,
                                                                         repNumber=repetition_counter)

                                triggered_alert_exist_flag = False
                                for item in triggered_error_list:
                                    if triggered_alert_to_add.alertId == item.alertId and \
                                            triggered_alert_to_add.repNumber == item.repNumber and \
                                            triggered_alert_to_add.stageNumber == item.stageNumber:
                                        triggered_alert_exist_flag = True
                                if not triggered_alert_exist_flag:
                                    triggered_error_list.append(triggered_alert_to_add)
                                    exercise_score -= calculateScore(
                                        starting_angle - tested_angle - exercise_instruction_loop.deviationNegative)

                                """# Save alerts that triggered during the exercise
                                triggered_error_list.append(
                                    TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                    repNumber=repetition_counter))
                                '''wrong_posture_image_to_display = alert_wrong_images[
                                    exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0'''
                                update_posture_image_flag = True

                                # ofir - score
                                if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                    exercise_score_frame_counter = 0
                                    exercise_score -= calculateScore(
                                        starting_angle - tested_angle - exercise_instruction_loop.deviationNegative)"""

                            if starting_angle + exercise_instruction_loop.deviationPositive <= tested_angle:
                                if starting_angle + exercise_instruction_loop.deviationPositive + exercise_instruction_loop.deviationNegative * -1 <= tested_angle:
                                    for item in instruction_alert_data_list:
                                        if item.alertId == exercise_instruction_loop.alertExtendedId:
                                            triggered_error_list_text.append(item.alertText)
                                            break

                                    '''triggered_error_list_text.append(
                                        instruction_alert_data_list[
                                            exercise_instruction_loop.alertExtendedId].alertText)'''
                                    error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                                    error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                                    triggered_alert_to_add = TriggeredAlerts(exercise_instruction_loop.alertId,
                                                                             stageNumber=current_stage,
                                                                             repNumber=repetition_counter)
                                    triggered_alert_exist_flag = False
                                    for item in triggered_error_list:
                                        if triggered_alert_to_add.alertId == item.alertId and \
                                                triggered_alert_to_add.repNumber == item.repNumber and \
                                                triggered_alert_to_add.stageNumber == item.stageNumber:
                                            triggered_alert_exist_flag = True
                                    if not triggered_alert_exist_flag:
                                        triggered_error_list.append(triggered_alert_to_add)
                                        exercise_score -= calculateScore(
                                            tested_angle - starting_angle + exercise_instruction_loop.deviationPositive + exercise_instruction_loop.deviationNegative * -1)

                                    """# Save alerts that triggered during the exercise
                                    triggered_error_list.append(
                                        TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                        repNumber=repetition_counter))
                                    '''wrong_posture_image_to_display = alert_wrong_images[
                                        exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0'''
                                    update_posture_image_flag = True

                                    # ofir - score
                                    if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                        exercise_score_frame_counter = 0
                                        exercise_score -= calculateScore(
                                            tested_angle - starting_angle + exercise_instruction_loop.deviationPositive + exercise_instruction_loop.deviationNegative * -1)"""
                                else:
                                    successful_exercise_instructions_in_current_stage += 1
                            continue

                        elif deviation_trigger_value == E_AlertDeviationTrigger.BOTH.value:
                            if tested_angle - exercise_instruction_loop.deviationPositive > starting_angle or \
                                    tested_angle - exercise_instruction_loop.deviationNegative < starting_angle:
                                triggered_error_list_text.append(current_instruction.instructionAlertData.alertText)
                                error_edges.append((current_instruction_v1_index, current_instruction_v2_index))
                                error_edges.append((current_instruction_v2_index, current_instruction_v3_index))

                                triggered_alert_to_add = TriggeredAlerts(exercise_instruction_loop.alertId,
                                                                         stageNumber=current_stage,
                                                                         repNumber=repetition_counter)

                                triggered_alert_exist_flag = False
                                for item in triggered_error_list:
                                    if triggered_alert_to_add.alertId == item.alertId and \
                                            triggered_alert_to_add.repNumber == item.repNumber and \
                                            triggered_alert_to_add.stageNumber == item.stageNumber:
                                        triggered_alert_exist_flag = True
                                if not triggered_alert_exist_flag:
                                    triggered_error_list.append(triggered_alert_to_add)
                                    exercise_score -= calculateScore(
                                        max(tested_angle - exercise_instruction_loop.deviationPositive,
                                            tested_angle - exercise_instruction_loop.deviationNegative))

                                """# Save alerts that triggered during the exercise
                                triggered_error_list.append(
                                    TriggeredAlerts(exercise_instruction_loop.alertId, stageNumber=current_stage,
                                                    repNumber=repetition_counter))
                                '''wrong_posture_image_to_display = alert_wrong_images[
                                    exercise_instruction_loop.alertId - 1]  # alert id starts from 1, array from 0'''
                                update_posture_image_flag = True

                                # ofir - score
                                if exercise_score_frame_counter % NUMBER_OF_FRAMES_BETWEEN_SCORE == 0:
                                    exercise_score_frame_counter = 0
                                    exercise_score -= calculateScore(
                                        max(tested_angle - exercise_instruction_loop.deviationPositive,
                                            tested_angle - exercise_instruction_loop.deviationNegative))"""

                            else:
                                successful_exercise_instructions_in_current_stage += 1
                            continue

                    if successful_exercise_instructions_in_current_stage == total_num_of_exercise_instructions_in_stage:
                        current_stage += repetition_direction
                        # update_goal_image_flag = True

                    if current_stage == exercise_stages:
                        if repetition_direction == 1:
                            repetition_counter += 1
                            self.RepetitionCounterUpdate.emit(repetition_counter)
                        repetition_direction = -1

                    elif current_stage == 1:
                        repetition_direction = 1

                except Exception as e:
                    print(e)
                    pass
                    # status image alerts

                # draw error landmarks
                mp_drawing.draw_landmarks(camera_image, results.pose_landmarks, set(error_edges),
                                          mp_drawing.DrawingSpec(color=(0, 117, 66), thickness=0,
                                                                 circle_radius=0),  # vertex color
                                          mp_drawing.DrawingSpec(color=(0, 66, 230), thickness=2,
                                                                 circle_radius=2)  # edges color
                                          )

                # Recolor camera image
                camera_image = cv2.cvtColor(camera_image, cv2.COLOR_BGR2RGB)
                camera_image = cv2.flip(camera_image, 1)

                # Resize image
                camera_image = cv2.resize(camera_image,
                                          (IMAGE_WIDTH, IMAGE_HEIGHT))

                # Camera image update
                CameraImagePic = QImage(camera_image.data, camera_image.shape[1],
                                        camera_image.shape[0], QImage.Format_RGB888)
                # CameraImagePic = ConvertToQtFormat.scaled(600, 600, Qt.KeepAspectRatio)
                self.CameraImageUpdate.emit(CameraImagePic)

                if update_posture_image_flag:
                    # Wrong posture image update
                    posture_image_to_display = wrong_posture_image_to_display
                else:
                    # Next stage posture
                    pass
                posture_image_to_display = stage_images[current_stage + repetition_direction - 1]

                posture_image_to_display = cv2.resize(posture_image_to_display,
                                                      (IMAGE_WIDTH, IMAGE_HEIGHT))
                posture_image_to_display = cv2.cvtColor(posture_image_to_display, cv2.COLOR_BGR2RGB)
                posture_image_to_display = QImage(posture_image_to_display.data,
                                                  posture_image_to_display.shape[1],
                                                  posture_image_to_display.shape[0], QImage.Format_RGB888)
                self.PostureImageUpdate.emit(posture_image_to_display)

                self.TriggeredAlertsUpdate.emit(triggered_error_list_text)

                if repetition_counter == self.repetition_num or exercise_score < 55:
                    # ToDo: Delete self.score
                    #       Set when there are no alerts at all
                    exercise_score = max(exercise_score, 0)
                    self.score = exercise_score
                    break

        cap.release()
        # Sort triggered error list and delete copies:
        triggered_error_list.sort(key=functools.cmp_to_key(compareTraineeTriggeredAlerts))

        triggered_error_list_no_dup = [triggered_error_list[0]]
        for item in triggered_error_list:
            if compareTraineeTriggeredAlerts(item, triggered_error_list_no_dup[-1]) != 0:  # if not equal
                triggered_error_list_no_dup.append(item)

        # Insert errors to table
        # Create feedback
        user_id = self.estimation_screen.getUserId()
        exercise_id = self.estimation_screen.getExerciseId()
        # -1 for placeholder
        exercise_feedback = Feedback(feedback_id=-1, user_id=user_id, exercise_id=exercise_id, date=datetime.now(),
                                     score=exercise_score, reps=self.repetition_num)
        # Insert new feedback
        feedback_id = DBConnection.createFeedBack(exercise_feedback)
        # set feedback id with correct feedback id that was returned from query
        exercise_feedback.feedback_id = feedback_id

        # Create logs for the feedback
        error_list_logs = []
        for item in triggered_error_list_no_dup:
            # -1 for placeholder - auto increment in DB
            current_error_log = FeedbackLog(log_id=-1, feedback_id=feedback_id, alert_id=item.alertId,
                                            stage_number=item.stageNumber, rep_number=item.repNumber)
            error_list_logs.append(current_error_log)

        # Insert all logs to DB
        DBConnection.createNewFeedbackLogs(error_list_logs)

        # Notify GUI score screen is ready
        self.ScoreScreenReadyUpdate.emit(feedback_id)
        self.quit()

# ToDo:  '''
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
