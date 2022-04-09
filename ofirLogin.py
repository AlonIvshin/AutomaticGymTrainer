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
        res = DBConnection.getUser('a')
        current_user = User(*res[0])
        myapp = App(current_user)
        myapp.show()
        self.close()
