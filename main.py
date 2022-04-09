import sys

import self as self

import ofirLogin
import welcomscreen
from PyQt5.QtWidgets import QApplication
from Utils import DBConnection
from ClassObjects.User import User

from workoutEstimation import EstimationScreen
from app import App

if __name__ == '__main__':
    app = QApplication([])
    '''#welcome = welcomscreen.WelcomeScreen()
    choose = chooseexercise.ChooseExerciseScreen()
    choose.show()
    #welcome.show()'''
    '''res = DBConnection.getUser('ofirvaknin55@gmail.com')
    current_user = User(*res[0])
    myapp = App(current_user)
    myapp.show()'''

    '''res = DBConnection.getUser('ofirvaknin55@gmail.com')
    current_user = User(*res[0])
    myapp = App(current_user)
    myapp.show()'''

    # EstimationScreen(exercise_id=1, repetition_num=3)
    # wo_est = EstimationScreen(1, 3)
    #wo_est.show()
    #welcome = welcomscreen.WelcomeScreen()
    #welcome.show()
    loginscr = ofirLogin.LoginScreen()
    loginscr.show()

    sys.exit(app.exec_())
