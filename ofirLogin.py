# QWidget
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QMainWindow, QLineEdit

from ClassObjects.User import User
from Utils import DBConnection
from app import App


class LoginScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./ui/ofirLogin.ui", self)
        self.setFixedSize(1000, 900)
        # self.txtBoxPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.btnLogin.clicked.connect(self.btnLoginAction)

    def btnLoginAction(self):
        # res = DBConnection.getUser('a')
        # current_user = User(*res[0])
        current_user = User(user_id=2, password='a', first_name='a', last_name='a', email='a', type='trainee',
                            phoneNumber='0546590043')
        myapp = App(current_user)
        myapp.show()
        '''self.close()'''
