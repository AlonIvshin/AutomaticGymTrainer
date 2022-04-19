import threading
import urllib

import PyQt5.QtCore as QtCore
import cv2
from PyQt5.QtCore import QAbstractTableModel, QSortFilterProxyModel
from PyQt5.QtGui import QImage, QPixmap

from ClassObjects.Exercise import Exercise
from Utils import DBConnection, WorkoutEstimationFunctions
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QTableView, QLineEdit, QWidget, QComboBox,QLabel
from numpy.core.defchararray import isnumeric

from workoutEstimation import EstimationScreen, WorkoutEstimationThread
from PyQt5.QtCore import Qt


def setAmericanScore(num):
    str = ''
    if int(num) < 55:
        str = 'F'
    if int(num) > 54:
        str = 'E'
    if int(num) > 64:
        str = 'D'
    if int(num) > 74:
        str = 'C'
    if int(num) > 84:
        str = 'B'
    if int(num) > 89:
        str = 'A'
    if int(num) > 94:
        str = 'A+'
    return str


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.table_data = data
        self.header_counter = 0  # ++ happens before using this index in headerData
        self.header_labels = ['']

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.table_data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self.table_data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.table_data[0])

    # implements the header that will be presented in the table view
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return str(self.header_labels[section])
        return super().headerData(section, orientation, role)

    def setHeaderList(self, headers):
        self.header_labels = headers


class AdminApp(QMainWindow):
    def __init__(self, current_user, widget):
        super().__init__()
        self.exercise = None
        self.ui = loadUi("./ui/appAdmin.ui", self)
        self.setFixedSize(1200, 800)
        self.current_user = current_user
        self.tabWidget.setCurrentIndex(0)  # sets default tab
        self.widget = widget

        # Tab #1 - Greetings
        self.lbl_welcome.setText('Welcome ' + current_user.first_name + ' ' + current_user.last_name)  # greeting user

        # Tab #2 - Exercise operations
        self.bt_addExerciseMngExercises.clicked.connect(self.addExercise)
        self.bt_deleteExerciseMngExercises.clicked.connect(self.deleteExercise)
        self.bt_clearFormMngExercises.clicked.connect(self.clearLabelsAndTextMngExercise)
        self.bt_saveChangesMngExercises.clicked.connect(self.saveEditedExercise)
        self.loadExercisesData()
        self.table_exercisesMngExercises.setColumnWidth(1, 80)
        self.table_exercisesMngExercises.setColumnWidth(0, 10)
        self.table_exercisesMngExercises.setColumnWidth(2, 200)
        self.table_exercisesMngExercises.setColumnHidden(0, True)
        self.table_exercisesMngExercises.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_exercisesMngExercises.clicked.connect(self.manageExerciseTableClicked)
        self.workoutEstimationWindow = None
        self.label_messagesMngExercises.hide()
        self.selected_exercise_id = -1

        # Tab #3 - Manage instructions
        # Set label image
        vertexes_image_url = 'https://i.imgur.com/C5eBW20.png'
        vertexes_image = WorkoutEstimationFunctions.getImageFromLink(vertexes_image_url)
        vertexes_image = cv2.resize(vertexes_image, (400, 400))
        vertexes_image = cv2.cvtColor(vertexes_image, cv2.COLOR_BGR2RGB)
        vertexes_image = QImage(vertexes_image,
                                vertexes_image.shape[1],
                                vertexes_image.shape[0], QImage.Format_RGB888)
        self.label_bodykeypointsMngInstructions.setPixmap(QPixmap.fromImage(vertexes_image))
        self.label_bodykeypointsMngInstructions.show()

        self.bt_addInstructionMngInstructions.clicked.connect(self.addInstruction)
        # self.bt_deleteInstructionMngInstructions.clicked.connect(self.deleteExercise)
        self.bt_clearInstructionMngInstructions.clicked.connect(self.clearLabelsAndTextMngInstructions)
        # self.bt_saveInstructionMngInstructions.clicked.connect(self.saveEditedExercise)
        self.loadInstructionData()
        self.selected_instruction_id = -1

    def loadExercisesData(self):
        headers = ['', 'Exercise Name', 'Main body part']
        self.exerciseData = DBConnection.getExerciesNamesAndTarget()
        self.exerciseData = sorted(self.exerciseData, key=lambda x: x[1])  # Sort data by exercise name
        self.exerciseModel = TableModel(self.exerciseData)
        self.exerciseModel.setHeaderList(headers)
        self.exercise_proxy_model = QSortFilterProxyModel()
        self.exercise_proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.exercise_proxy_model.setSourceModel(self.exerciseModel)
        self.exercise_proxy_model.sort(0, Qt.AscendingOrder)
        self.table_exercisesMngExercises.setModel(self.exercise_proxy_model)
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        self.lineEdit_searchBarMngExercises.textChanged.connect(self.exercise_proxy_model.setFilterFixedString)

    def loadInstructionData(self):
        headers = ['','Vertex1', 'Vertex2', 'Vertex3', 'Angle', 'Description', 'Axis']
        self.instructionData = DBConnection.getAllInstructions()
        self.instructionData = sorted(self.instructionData, key=lambda x: x[1])  # Sort data by exercise name
        for index in range(len(self.instructionData)): # to remove instruction index duplication in the table
            self.instructionData[index] = self.instructionData[index][1:]
        self.instructionModel = TableModel(self.instructionData)
        self.instructionModel.setHeaderList(headers)
        self.instruction_proxy_model = QSortFilterProxyModel()
        self.instruction_proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.instruction_proxy_model.setSourceModel(self.instructionModel)
        self.instruction_proxy_model.sort(0, Qt.AscendingOrder)
        self.table_instructionsMngInstructions.setModel(self.instruction_proxy_model)
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        self.lineEdit_searchBarManageInstructions.textChanged.connect(self.instruction_proxy_model.setFilterFixedString)

    def clearLabelsAndTextMngExercise(self):
        self.lineEdit_enameMngExercises.setText('')
        self.plainTextEdit_descriptionMngExercises.clear()
        self.lineEdit_stagenumMngExercises.setText('')
        self.lineEdit_videolinkMngExercises.setText('')
        self.lineEdit_mainTargetMngExercises.setText('')
        self.label_messagesMngExercises.setText('')
        self.selected_exercise_id = -1

    def clearLabelsAndTextMngInstructions(self):
        self.lineEdit_angleMngInstructions.setText('')
        self.plainTextEdit_descriptionMngInstructions.clear()
        # How to set default value for combo box
        self.comboBox_vertex1MngInstructions.setText('')
        self.comboBox_vertex2MngInstructions.setText('')
        self.comboBox_vertex3MngInstructions.setText('')
        self.comboBox_axisMngInstructions.setText('')
        self.label_messagesMngInstructions.setText('')
        self.selected_instruction_id = -1

    # Check if there are any empty fields
    def checkEmptyFieldMngExercise(self):
        return self.lineEdit_enameMngExercises.text() == '' or self.lineEdit_videolinkMngExercises.text() == '' or self.plainTextEdit_descriptionMngExercises.toPlainText() == '' or self.lineEdit_stagenumMngExercises.text() == '' or self.lineEdit_mainTargetMngExercises.text() == ''

    # Save changes done with edit exercise
    def saveEditedExercise(self):
        if self.selected_exercise_id == -1:
            self.label_messagesMngExercises.setText("Please choose exercise")
            self.label_messagesMngExercises.show()
            return
        maxCurrentStage = DBConnection.getMaxStageInExercise(self.selected_exercise_id)
        if self.checkEmptyFieldMngExercise():
            self.label_messagesMngExercises.setText("Make sure all fields are filled")
        elif self.selected_exercise_id < maxCurrentStage:
            self.label_messagesMngExercises.setText(f"Existing instruction has stage number of {maxCurrentStage}!")
        else:
            exercise = Exercise(self.selected_exercise_id, self.lineEdit_enameMngExercises.text(),
                                self.lineEdit_videolinkMngExercises.text(),
                                self.plainTextEdit_descriptionMngExercises.toPlainText(),
                                self.lineEdit_stagenumMngExercises.text()
                                , self.lineEdit_mainTargetMngExercises.text())
            self.exercise = exercise

            res = DBConnection.modifyExercise(exercise)

    def editExercise(self):
        if self.selected_exercise_id == -1:
            self.label_messagesMngExercises.setText("Please choose exercise")
            self.label_messagesMngExercises.show()
        else:
            res = DBConnection.getExercise(self.selected_exercise_id)
            self.exercise = Exercise(*res[0])
            exercise = self.exercise
            self.lineEdit_enameMngExercises.setText(str(exercise.exercise_name))
            self.plainTextEdit_descriptionMngExercises.setPlainText(str(exercise.description))
            self.lineEdit_stagenumMngExercises.setText(str(exercise.num_of_stages))
            self.lineEdit_videolinkMngExercises.setText(str(exercise.video))
            self.lineEdit_mainTargetMngExercises.setText(str(exercise.main_target))

    def addExercise(self):
        if self.checkEmptyFieldMngExercise():
            self.label_messagesMngExercises.setText("Make sure all fields are filled")
            self.label_messagesMngExercises.show()
            return
        exercise = Exercise(-1, self.lineEdit_enameMngExercises.text(), self.lineEdit_videolinkMngExercises.text(),
                            self.plainTextEdit_descriptionMngExercises.toPlainText(),
                            self.lineEdit_stagenumMngExercises.text()
                            , self.lineEdit_mainTargetMngExercises.text())
        res = DBConnection.addNewExercise(exercise)
        if res:
            self.label_messagesMngExercises.setText("Exercise added")
            self.label_messagesMngExercises.show()
            self.loadExercisesData()

    def addInstruction(self):
        if self.checkEmptyFieldMngExercise():
            self.label_messagesMngExercises.setText("Make sure all fields are filled")
            self.label_messagesMngExercises.show()
            return
        exercise = Exercise(-1, self.lineEdit_enameMngExercises.text(), self.lineEdit_videolinkMngExercises.text(),
                            self.plainTextEdit_descriptionMngExercises.toPlainText(),
                            self.lineEdit_stagenumMngExercises.text()
                            , self.lineEdit_mainTargetMngExercises.text())
        res = DBConnection.addNewExercise(exercise)
        if res:
            self.label_messagesMngExercises.setText("Exercise added")
            self.label_messagesMngExercises.show()
            self.loadExercisesData()

    def deleteExercise(self):
        pass

    def startEstimationFunction(self):
        e_id = self.i_eid.text()
        r_num = self.i_repsnum.text()
        if isnumeric(e_id) and isnumeric(r_num):
            self.workoutEstimationWindow = EstimationScreen(exercise_id=e_id, repetition_num=r_num, widget=self.widget,
                                                            user_id=self.current_user.user_id)
            self.widget.addWidget(self.workoutEstimationWindow)
            self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
            # self.workoutEstimationWindow.show()
            # self.close() #Problem here

            # self.bt_start.clicked.connect(lambda: EstimationScreen(e_id, r_num))

        else:
            self.lbl_alert.show()
            self.lbl_chosen.hide()

    # Loads data to manage exercises tab (exercise name, main body part)
    def loadExerciseData(self):
        res = DBConnection.getExerciesNamesAndTarget()
        for row_number, row_data in enumerate(res):
            self.table_exercisesMngExercises.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table_exercisesMngExercises.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    '''def loadDataHistory(self, user_id):
        # workout history
        res = DBConnection.getCurrentUserFeedbacks(user_id)
        allfeedbacks = [FeedbackHistory(*x) for x in res]
        if len(allfeedbacks) > 3:  # we want to see in the table feedbacks only from the 4th feedback (need to be > 3)
            for row_number, row_data in enumerate(res[3:]):  # res[3:]
                self.table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        # presenting the 3 first feedbacks
        for index, feed in enumerate(allfeedbacks):
            name = getattr(self.ui, 'lbl_name{}'.format(index + 1))
            reps = getattr(self.ui, 'lbl_reps{}'.format(index + 1))
            date = getattr(self.ui, 'lbl_date{}'.format(index + 1))
            score = getattr(self.ui, 'lbl_score{}'.format(index + 1))
            img = getattr(self.ui, 'image{}'.format(index + 1))
    
            name.setText(str(feed.exercise_name))
            reps.setText("Number of reps: " + str(feed.reps))
            date.setText(str(feed.date))
            score.setText(setAmericanScore(feed.score))
    
            name.show()
            reps.show()
            date.show()
            img.show()
            score.show()'''

    def manageExerciseTableClicked(self):
        index = self.table_exercisesMngExercises.currentIndex()
        newIndex = self.table_exercisesMngExercises.exerciseModel().index(index.row(), 0)
        newIndex2 = self.table_exercisesMngExercises.exerciseModel().index(index.row(), 1)

        self.selected_exercise_id = self.table_exercisesMngExercises.exerciseModel().exerciseData(
            newIndex)  # we can pass eid to the model
        txt = self.table_exercisesMngExercises.exerciseModel().exerciseData(newIndex2)
        self.label_messagesMngExercises.setText(txt + " is chosen")
        self.label_messagesMngExercises.show()

        self.editExercise()


'''def openInstructionsWindow(self):
    if self.i_eid.text() != '':
        vid_id = DBConnection.getVideoId(self.i_eid.text())
        ins = WatchExerciseInstructions(vid_id, self.i_eid.text())
        ins.show()
        self.lbl_alert.hide()
    else:
        self.lbl_alert.show()'''

'''def closeEvent(self, event):
    print("The user: " + self.current_user.first_name + ' ' + self.current_user.last_name + ' ' + "logged out!")
    DBConnection.logOutCurrentUser(self.current_user.user_id)'''

# ToDo:
'''
   Check that delete exercise is working - delete all instructions as well?
'''
