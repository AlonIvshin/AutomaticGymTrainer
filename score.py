from Utils import DBConnection
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTableWidgetItem
from PyQt5.uic import loadUi


def loadMyScore(feedback_id):
    return str(DBConnection.getFeedbackScore(feedback_id))


class Feedback(QMainWindow):
    def __init__(self, feedback_id):
        super().__init__()
        self.ui = loadUi("./ui/score.ui", self)
        self.lbl_score.setText(loadMyScore(feedback_id))  # change arg to 'feedback_id'
        self.lbl_score.show()
        self.tb_mistakes.setColumnWidth(1, 150)
        self.tb_mistakes.setColumnWidth(0, 600)
        self.tb_mistakes.setColumnWidth(2, 150)
        self.tb_mistakes.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.loadData(feedback_id)
        self.setAmericanScore()

    def loadData(self,feedback_id):
        res = DBConnection.getFeedbackLogData(feedback_id)
        for row_number, row_data in enumerate(res):
            self.tb_mistakes.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tb_mistakes.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def setAmericanScore(self):
        if int(self.lbl_score.text()) < 55:
            self.lbl_american_score.setText('F')
        if int(self.lbl_score.text()) > 54:
            self.lbl_american_score.setText('E')
        if int(self.lbl_score.text()) > 64:
            self.lbl_american_score.setText('D')
        if int(self.lbl_score.text()) > 74:
            self.lbl_american_score.setText('C')
        if int(self.lbl_score.text()) > 84:
            self.lbl_american_score.setText('B')
        if int(self.lbl_score.text()) > 89:
            self.lbl_american_score.setText('A')
        if int(self.lbl_score.text()) > 94:
            self.lbl_american_score.setText('A+')

