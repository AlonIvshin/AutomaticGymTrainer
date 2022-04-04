from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from login import Login
from createacc import CreateAcc


class WelcomeScreen(QMainWindow):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("./ui/welcomescreen.ui", self)
        self.setFixedSize(1200, 800)
        self.bt_login.clicked.connect(self.openLoginWindow)
        self.bt_signup.clicked.connect(self.openCreateAccountWindow)

    def openLoginWindow(self):
        login = Login()
        login.show()
        self.close()

    def openCreateAccountWindow(self):
        ca = CreateAcc()
        ca.show()
        self.close()

    def closeEvent(self, event):
        print("X Pressed!")
