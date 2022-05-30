import ctypes
import sys

from PyQt5 import QtWidgets

import welcomscreen
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui
from score import FeedbackScreen
from Utils import DBConnection
from ClassObjects.User import User
from appAdmin import AdminApp
from app import App
from login import Login
import workouthistory

from workoutEstimation import EstimationScreen

if __name__ == '__main__':
    myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication([])

    widget = QtWidgets.QStackedWidget()
    widget.setWindowTitle("Automatic Gym Trainer")
    widget.setWindowIcon(QtGui.QIcon('etc/coach.png'))
    welcome = welcomscreen.WelcomeScreen(widget)

    #welcome.showFullScreen()
    #welcome = FeedbackScreen(feedback_id='14',widget=widget)
    #res = DBConnection.getUser('a')
    #current_user =User(*res[0])
    #welcome = AdminApp(current_user, widget)
    widget.addWidget(welcome)
    widget.showMaximized()
    widget.show()

    # ToDo: press on click crash

    '''widget = QtWidgets.QStackedWidget()
    welcome = workouthistory.WorkoutHistory(widget)
    widget.addWidget(welcome)
    widget.show()'''


    sys.exit(app.exec_())
