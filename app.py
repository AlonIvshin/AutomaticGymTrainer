from Utils import DBConnection
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
from numpy.core.defchararray import isnumeric

from WatchExerciseInstructions import WatchExerciseInstructions
from workoutEstimation import EstimationScreen, WorkoutEstimationThread


class App(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        # super(App, self,current_user).__init__()
        self.ui = loadUi("./ui/app.ui", self)
        self.setFixedSize(1200, 800)
        self.current_user = current_user
        self.lbl_welcome.setText('Welcome ' + current_user.first_name + ' ' + current_user.last_name)  # greating user
        self.bt_start.clicked.connect(self.startEstimationFunction)
        self.bt_watch.clicked.connect(self.openInstructionsWindow)
        self.loaddata()
        # self.table.setFixedWidth(self.table.columnWidth(0) + self.table.columnWidth(1)+ self.table.ver)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(0, 10)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.clicked.connect(self.doubleClicked_table)
        self.workoutEstimationWindow = None
        self.my_thread = None
        self.lbl_alert.hide()
        self.show()

    def startEstimationFunction(self):
        e_id = self.i_eid.text()
        r_num = self.i_repsnum.text()
        if isnumeric(e_id) and isnumeric(r_num):

            self.workoutEstimationWindow = EstimationScreen(exercise_id=e_id, repetition_num=r_num)
            self.workoutEstimationWindow.show()

            #self.close()
            # self.bt_start.clicked.connect(lambda: EstimationScreen(e_id, r_num))
        else:
            self.lbl_alert.show()

    def loaddata(self):
        res = DBConnection.getExerciesNamesAndTarget()
        for row_number, row_data in enumerate(res):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def doubleClicked_table(self):
        index = self.table.currentIndex()
        newIndex = self.table.model().index(index.row(), 0)
        eid = self.table.model().data(newIndex)  # we can pass eid to the model
        self.i_eid.setText(eid)

    def openInstructionsWindow(self):
        if self.i_eid.text() != '':
            vid_id = DBConnection.getVideoId(self.i_eid.text())
            ins = WatchExerciseInstructions(vid_id, self.i_eid.text())
            ins.show()
            self.lbl_alert.hide()
        else:
            self.lbl_alert.show()

    def closeEvent(self, event):
        print("The user: " + self.current_user.first_name + ' ' + self.current_user.last_name + ' ' + "logged out!")
        DBConnection.logOutCurrentUser(self.current_user.user_id)
