import threading

import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QAbstractTableModel, QSortFilterProxyModel

from ClassObjects.Exercise import Exercise
from Utils import DBConnection
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QTableView, QLineEdit, QWidget
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
        self.header_labels = ['', 'Exercise Name', 'Main body part']

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


class AdminApp(QMainWindow):
    def __init__(self, current_user, widget):
        super().__init__()
        self.exercise = None
        self.ui = loadUi("./ui/appAdmin.ui", self)
        self.setFixedSize(1200, 800)
        self.current_user = current_user
        self.tabWidget.setCurrentIndex(0)  # sets default tab

        # Tab #1 - Greetings
        self.lbl_welcome.setText('Welcome ' + current_user.first_name + ' ' + current_user.last_name)  # greeting user

        # Tab #2 - Exercise operations
        self.bt_addExercise.clicked.connect(self.addExercise)
        self.bt_deleteExercise.clicked.connect(self.deleteExercise)
        self.bt_clearForm.clicked.connect(self.clearLabelsAndText)
        self.bt_saveChanges.clicked.connect(self.saveEditedExercise)

        self.loadExercisesData()

        '''self.data = DBConnection.getExerciesNamesAndTarget()
        self.data = sorted(self.data, key=lambda x: x[1])  # Sort data by exercise name
        self.model = TableModel(self.data)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.sort(0, Qt.AscendingOrder)
        self.table_manageExercises.setModel(self.proxy_model)'''

        '''# You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        self.lineEdit_searchBarManageExercise.textChanged.connect(self.proxy_model.setFilterFixedString)'''

        self.table_manageExercises.setColumnWidth(1, 80)
        self.table_manageExercises.setColumnWidth(0, 10)
        self.table_manageExercises.setColumnWidth(2, 200)
        self.table_manageExercises.setColumnHidden(0, True)
        self.table_manageExercises.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_manageExercises.clicked.connect(self.manageExerciseTableClicked)
        self.workoutEstimationWindow = None
        self.label_messagesMngExercise.hide()
        self.widget = widget

        self.selected_exercise_id = -1

        # Workout History
        ''' for num in range(1, 4):
            name = getattr(self.ui, 'lbl_name{}'.format(num))
            reps = getattr(self.ui, 'lbl_reps{}'.format(num))
            date = getattr(self.ui, 'lbl_date{}'.format(num))
            score = getattr(self.ui, 'lbl_score{}'.format(num))
            img = getattr(self.ui, 'image{}'.format(num))
            name.hide()
            reps.hide()
            date.hide()
            score.hide()
            img.hide()'''
        # self.loadDataHistory(self.current_user.user_id)  # need to change to user id

    def loadExercisesData(self):
        self.data = DBConnection.getExerciesNamesAndTarget()
        self.data = sorted(self.data, key=lambda x: x[1])  # Sort data by exercise name
        self.model = TableModel(self.data)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.sort(0, Qt.AscendingOrder)
        self.table_manageExercises.setModel(self.proxy_model)
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        self.lineEdit_searchBarManageExercise.textChanged.connect(self.proxy_model.setFilterFixedString)

    def clearLabelsAndText(self):
        self.lineEdit_ename.setText('')
        self.plainTextEdit_description.clear()
        self.lineEdit_stagenum.setText('')
        self.lineEdit_videolink.setText('')
        self.lineEdit_mainTarget.setText('')
        self.label_messagesMngExercise.setText('')
        self.selected_exercise_id = -1

    # Check if there are any empty fields
    def checkEmptyField(self):
        return self.lineEdit_ename.text() == '' or self.lineEdit_videolink.text() == '' or self.plainTextEdit_description.toPlainText() == '' or self.lineEdit_stagenum.text() == '' or self.lineEdit_mainTarget.text() == ''

    # Save changes done with edit exercise
    def saveEditedExercise(self):
        if self.selected_exercise_id == -1:
            self.label_messagesMngExercise.setText("Please choose exercise")
            self.label_messagesMngExercise.show()
            return
        maxCurrentStage = DBConnection.getMaxStageInExercise(self.selected_exercise_id)
        if self.checkEmptyField():
            self.label_messagesMngExercise.setText("Make sure all fields are filled")
        elif self.selected_exercise_id < maxCurrentStage:
            self.label_messagesMngExercise.setText(f"Existing instruction has stage number of {maxCurrentStage}!")
        else:
            exercise = Exercise(self.selected_exercise_id, self.lineEdit_ename.text(), self.lineEdit_videolink.text(),
                                self.plainTextEdit_description.toPlainText(), self.lineEdit_stagenum.text()
                                , self.lineEdit_mainTarget.text())
            self.exercise = exercise

            res = DBConnection.modifyExercise(exercise)

    def editExercise(self):
        if self.selected_exercise_id == -1:
            self.label_messagesMngExercise.setText("Please choose exercise")
            self.label_messagesMngExercise.show()
        else:
            res = DBConnection.getExercise(self.selected_exercise_id)
            self.exercise = Exercise(*res[0])
            exercise = self.exercise
            self.lineEdit_ename.setText(str(exercise.exercise_name))
            self.plainTextEdit_description.setPlainText(str(exercise.description))
            self.lineEdit_stagenum.setText(str(exercise.num_of_stages))
            self.lineEdit_videolink.setText(str(exercise.video))
            self.lineEdit_mainTarget.setText(str(exercise.main_target))

    def addExercise(self):
        if self.checkEmptyField():
            self.label_messagesMngExercise.setText("Make sure all fields are filled")
            self.label_messagesMngExercise.show()
            return
        exercise = Exercise(-1, self.lineEdit_ename.text(), self.lineEdit_videolink.text(),
                            self.plainTextEdit_description.toPlainText(), self.lineEdit_stagenum.text()
                            , self.lineEdit_mainTarget.text())
        res = DBConnection.addNewExercise(exercise)
        if res:
            self.label_messagesMngExercise.setText("Exercise added")
            self.label_messagesMngExercise.show()
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
            self.table_manageExercises.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table_manageExercises.setItem(row_number, column_number, QTableWidgetItem(str(data)))

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
        index = self.table_manageExercises.currentIndex()
        newIndex = self.table_manageExercises.model().index(index.row(), 0)
        newIndex2 = self.table_manageExercises.model().index(index.row(), 1)

        self.selected_exercise_id = self.table_manageExercises.model().data(newIndex)  # we can pass eid to the model
        txt = self.table_manageExercises.model().data(newIndex2)
        self.label_messagesMngExercise.setText(txt + " is chosen")
        self.label_messagesMngExercise.show()

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
