from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from login import Login


class WelcomeScreen(QMainWindow):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("./ui/welcomescreen.ui", self)
        self.setFixedSize(1200, 800)
        self.bt_login.clicked.connect(self.openLoginWindow)

    def openLoginWindow(self):
        login = Login()
        login.show()
        self.close()

    def closeEvent(self, event):
        print("X Pressed!")
