import threading

from Utils import DBConnection
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
from numpy.core.defchararray import isnumeric

from WatchExerciseInstructions import WatchExerciseInstructions
from workoutEstimation import EstimationScreen, WorkoutEstimationThread
from ClassObjects.Feedback import Feedback, FeedbackHistory


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


class AdminApp(QMainWindow):
    def __init__(self, current_user, widget):
        super().__init__()
        self.ui = loadUi("./ui/appAdmin.ui", self)
        self.setFixedSize(1200, 800)
        self.current_user = current_user
        self.tabWidget.setCurrentIndex(0)  # sets default tab
        # Main
        self.lbl_welcome.setText('Welcome ' + current_user.first_name + ' ' + current_user.last_name)  # greeting user
        # Choose Exercise
        self.bt_editExercise.clicked.connect(self.editExercise)  # Should open new window to edit basic information of the exercise
        self.bt_addExercise.clicked.connect(self.addExercise)
        self.bt_deleteExercise.clicked.connect(self.deleteExercise)
        self.loaddata()  # load all exercises
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(0, 10)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.clicked.connect(self.doubleClicked_table)
        self.workoutEstimationWindow = None
        self.label_messagesMngExercise.hide()
        self.widget = widget
        #self.i_eid.hide()
        #self.label_3.hide()
        #self.lbl_chosen.hide()

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
        #self.loadDataHistory(self.current_user.user_id)  # need to change to user id

    def editExercise(self):
        pass

    def addExercise(self):
        pass

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
    def loaddata(self):
        res = DBConnection.getExerciesNamesAndTarget()
        for row_number, row_data in enumerate(res):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

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

    def doubleClicked_table(self):
        index = self.tb_ce.currentIndex()
        newIndex = self.tb_ce.model().index(index.row(), 0)
        newIndex2 = self.tb_ce.model().index(index.row(), 1)
        eid = self.tb_ce.model().data(newIndex)  # we can pass eid to the model
        txt = self.tb_ce.model().data(newIndex2)
        self.i_eid.setText(eid)
        self.lbl_chosen.setText(txt + " is chosen")
        self.lbl_chosen.show()

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
