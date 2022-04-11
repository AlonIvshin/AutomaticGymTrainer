import sys

from PyQt5 import QtWidgets

import ofirLogin
import welcomscreen
from PyQt5.QtWidgets import QApplication
from Utils import DBConnection
from ClassObjects.User import User
from app import App
from login import Login

from workoutEstimation import EstimationScreen

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

    '''current_user = User(user_id=2, password='a', first_name='a', last_name='a', email='a', type='trainee',
                        phoneNumber='0546590043')
    myapp = App(current_user)'''
    '''myapp.show()'''
    widget = QtWidgets.QStackedWidget()
    welcome = welcomscreen.WelcomeScreen(widget)
    widget.addWidget(welcome)
    widget.show()

    sys.exit(app.exec_())
