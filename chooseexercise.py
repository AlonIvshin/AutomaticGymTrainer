from PyQt5 import QtWidgets
from est import my_est
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
import DBConnection
from numpy.core.defchararray import isnumeric


class ChooseExerciseScreen(QMainWindow):
    def __init__(self):
        super(ChooseExerciseScreen, self).__init__()
        loadUi("./ui/chooseexercise.ui", self)
        self.setFixedSize(1200, 800)
        self.bt_start.clicked.connect(self.startEstimationFunction)
        self.loaddata()
        # self.table.setFixedWidth(self.table.columnWidth(0) + self.table.columnWidth(1)+ self.table.ver)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(0, 10)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.clicked.connect(self.doubleClicked_table)
        self.lbl_alert.hide()

    def startEstimationFunction(self):
        e_id = self.i_eid.text()
        r_num = self.i_repsnum.text()
        if isnumeric(e_id) and isnumeric(r_num):
            self.bt_start.clicked.connect(my_est(e_id, r_num))
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
