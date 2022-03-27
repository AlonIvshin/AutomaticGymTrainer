from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow


class WelcomeScreen(QMainWindow):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        self.setFixedSize(1200, 800)

