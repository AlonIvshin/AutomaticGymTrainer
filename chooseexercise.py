from est import my_est
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow



class ChooseExerciseScreen(QMainWindow):
    def __init__(self):
        super(ChooseExerciseScreen, self).__init__()
        loadUi("chooseexercise.ui", self)
        self.setFixedSize(1200, 800)
        self.bt_start.clicked.connect(self.startEstimationFunction)


    def startEstimationFunction(self):
        e_id = self.i_eid.text()
        r_num = self.i_repsnum.text()
        self.bt_start.clicked.connect(my_est(e_id, r_num))