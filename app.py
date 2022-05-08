import threading

import requests
from PyQt5.QtGui import QImage, QPixmap

from Utils import DBConnection
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
from numpy.core.defchararray import isnumeric

from WatchExerciseInstructions import WatchExerciseInstructions
from score import FeedbackScreen
from workoutEstimation import EstimationScreen, WorkoutEstimationThread
from ClassObjects.Feedback import Feedback,FeedbackHistory
import webbrowser


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

class App(QMainWindow):
    def __init__(self, current_user, widget):
        super().__init__()
        self.ui = loadUi("./ui/app.ui", self)
        self.setFixedSize(1920, 1000)
        self.current_user = current_user
        self.tabWidget.setCurrentIndex(0)  # sets default tab
        # LOAD TAB WIDGET CSS FILE
        with open('ui/tab.css', "r") as fh:
            tw = fh.read()
            self.tabWidget.setStyleSheet(tw)
        #Main
        self.lbl_welcome.setText('Welcome ' + current_user.first_name + ' ' + current_user.last_name)  # greating user
        self.lbl_workouts_num.setText(str(DBConnection.getWorkoutsQuantity(current_user.user_id)) + ' workout sessions')
        self.lbl_avg.setText(str(DBConnection.getWorkoutsAVG(current_user.user_id)))
        self.bt_word.clicked.connect(self.openHelpWord)
        #Choose Exercise
        self.bt_start.clicked.connect(self.startEstimationFunction)
        self.bt_watch.clicked.connect(self.openInstructionsWindow)
        self.loaddata()
        # self.table.setFixedWidth(self.table.columnWidth(0) + self.table.columnWidth(1)+ self.table.ver)
        self.tb_ce.setColumnWidth(1, 80)
        self.tb_ce.setColumnWidth(0, 10)
        self.tb_ce.setColumnWidth(2, 200)
        self.tb_ce.setColumnHidden(0, True)
        self.tb_ce.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tb_ce.clicked.connect(self.doubleClicked_table)
        self.workoutEstimationWindow = None
        self.lbl_alert.hide()
        self.widget = widget
        self.i_eid.hide()
        self.label_3.hide()
        self.lbl_chosen.hide()

        #Workout History
        self.table.doubleClicked.connect(self.doubleClicked_FeedbackTable) # << MEARGE ME 190422
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        for num in range(1, 4):
            name = getattr(self.ui, 'lbl_name{}'.format(num))
            reps = getattr(self.ui, 'lbl_reps{}'.format(num))
            date = getattr(self.ui, 'lbl_date{}'.format(num))
            score = getattr(self.ui, 'lbl_score{}'.format(num))
            img = getattr(self.ui, 'image{}'.format(num))
            name.hide()
            reps.hide()
            date.hide()
            score.hide()
            img.hide()
        self.loadDataHistory(self.current_user.user_id)  # need to change to user id

    def startEstimationFunction(self):
        e_id = self.i_eid.text()
        r_num = self.i_repsnum.text()
        if isnumeric(e_id) and isnumeric(r_num):
            self.workoutEstimationWindow = EstimationScreen(exercise_id=e_id, repetition_num=r_num, widget = self.widget, user_id=self.current_user.user_id)
            self.widget.addWidget(self.workoutEstimationWindow)
            self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
            #self.workoutEstimationWindow.show()
            #self.close() #Problem here

            # self.bt_start.clicked.connect(lambda: EstimationScreen(e_id, r_num))

        else:
            self.lbl_alert.show()
            self.lbl_chosen.hide()

    def loaddata(self):
        res = DBConnection.getExerciesNamesAndTarget()
        for row_number, row_data in enumerate(res):
            self.tb_ce.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tb_ce.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def loadMain(self,user_id):
        self.lbl_workouts_num.setText(str(DBConnection.getWorkoutsQuantity(user_id)) + ' workout sessions')
        self.lbl_avg.setText(str(DBConnection.getWorkoutsAVG(user_id)))
    def loadDataHistory(self, user_id):
        #workout history
        res = DBConnection.getCurrentUserFeedbacks(user_id)
        allfeedbacks = [FeedbackHistory(*x) for x in res]
        pre_table_range = len(res)
        if len(res) > 3:  # we want to see in the table feedbacks only from the 4th feedback (need to be > 3)
            pre_table_range = 3
            for row_number, row_data in enumerate(res[3:]):  # res[3:]
                self.table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        # presenting the 3 first feedbacks
        for index, feed in enumerate(allfeedbacks[:pre_table_range]):
            name = getattr(self.ui, 'lbl_name{}'.format(index + 1))
            reps = getattr(self.ui, 'lbl_reps{}'.format(index + 1))
            date = getattr(self.ui, 'lbl_date{}'.format(index + 1))
            score = getattr(self.ui, 'lbl_score{}'.format(index + 1))
            img = getattr(self.ui, 'image{}'.format(index + 1))

            # << MEARGE ME 190422
            #img.mousePressEvent = (lambda x: self.doubleClicked_Image(allfeedbacks[index].feedback_id))
            # << END MEARGE ME 190422

            name.setText(str(feed.exercise_name))
            reps.setText("Number of reps: " + str(feed.reps))
            date.setText(str(feed.date))
            score.setText(setAmericanScore(feed.score))

            img.setScaledContents(True)
            image = QImage()
            image.loadFromData(requests.get(DBConnection.getImageForFeedback(feed.feedback_id)).content)
            img.setPixmap(QPixmap(image))

            name.show()
            reps.show()
            date.show()
            img.show()
            score.show()

        # << MEARGE ME 190422
           #self.bt_watch_2.clicked.connect(self.doubleClicked_Image)
        if len(res) > 0:
            self.image1.mousePressEvent = (lambda x: self.doubleClicked_Image(allfeedbacks[0].feedback_id))
        if len(res) > 1:
            self.image2.mousePressEvent = (lambda x: self.doubleClicked_Image(allfeedbacks[1].feedback_id))
        if len(res) > 2:
            self.image3.mousePressEvent = (lambda x: self.doubleClicked_Image(allfeedbacks[2].feedback_id))
            # << MEARGE ME 190422 END

    def doubleClicked_Image(self, feedback_id):
        score = FeedbackScreen(str(feedback_id), self.widget)
        self.widget.addWidget(score)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    def doubleClicked_table(self):
        index = self.tb_ce.currentIndex()
        newIndex = self.tb_ce.model().index(index.row(), 0) # << MEARGE ME 190422
        newIndex2 = self.tb_ce.model().index(index.row(), 1)# << MEARGE ME 190422
        eid = self.tb_ce.model().data(newIndex)  # we can pass eid to the model # << MEARGE ME 190422
        txt = self.tb_ce.model().data(newIndex2) # << MEARGE ME 190422
        self.i_eid.setText(eid)
        self.lbl_chosen.setText(txt + " is chosen")
        self.lbl_chosen.show()


    def doubleClicked_FeedbackTable(self): # << MEARGE ME 190422
        index = self.table.currentIndex()
        newIndex = self.table.model().index(index.row(), 0)
        fid = self.table.model().data(newIndex)  # we can pass eid to the model
        self.doubleClicked_Image(fid)

    def openInstructionsWindow(self):
        if self.i_eid.text() != '':
            vid_id = DBConnection.getVideoId(self.i_eid.text())
            ins = WatchExerciseInstructions(vid_id, self.i_eid.text())
            ins.show()
            self.lbl_alert.hide()
        else:
            self.lbl_alert.show()



    def openHelpWord(self):
        webbrowser.open('https://docs.google.com/document/d/1S7cyPW_vhBwGGffrBhwWfTJKKJYkiSb5Jm9SXeCZ-Wg/edit?usp=sharing%27')



    '''def closeEvent(self, event):
        print("The user: " + self.current_user.first_name + ' ' + self.current_user.last_name + ' ' + "logged out!")
        DBConnection.logOutCurrentUser(self.current_user.user_id)'''
