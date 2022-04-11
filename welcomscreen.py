from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from login import Login
from createacc import CreateAcc


class WelcomeScreen(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        self.ui = loadUi("./ui/welcomescreen.ui", self)
        self.setFixedSize(1000, 700)
        self.bt_login.clicked.connect(self.openLoginWindow)
        self.bt_signup.clicked.connect(self.openCreateAccountWindow)
        self.widget = widget

    def openLoginWindow(self):
        login = Login(self.widget)
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        #login.show()
        #self.close()

    def openCreateAccountWindow(self):
        ca = CreateAcc()
        ca.show()
        self.close()

    def closeEvent(self, event):
        print("X Pressed!")
