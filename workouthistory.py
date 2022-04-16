from Utils import DBConnection
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTableWidgetItem
from PyQt5.uic import loadUi
from ClassObjects.Feedback import Feedback


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


class WorkoutHistory(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.ui = loadUi("./ui/workouthistory.ui", self)
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
        self.loadData(1)  # need to change to user id

    def loadData(self, user_id):
        res = DBConnection.getCurrentUserFeedbacks(user_id)
        allfeedbacks = [Feedback(*x) for x in res]
        if len(allfeedbacks) > 0:  # we want to see in the table feedbacks only from the 4th feedback (need to be > 3)
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
            reps.setText(str(feed.reps))
            date.setText(str(feed.date))
            score.setText(setAmericanScore(feed.score))

            name.show()
            reps.show()
            date.show()
            img.show()
            score.show()
