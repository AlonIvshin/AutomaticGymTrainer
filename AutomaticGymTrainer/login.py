from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from createacc import CreateAcc
from Utils import DBConnection
from ourclasses import User
from app import App



class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("./ui/login.ui", self)
        self.bt_click.clicked.connect(self.openCreateAccountWindow)
        self.bt_login.clicked.connect(self.login)
        self.lbl_fields.hide()
        self.lbl_loged.hide()
        self.lbl_incorrect.hide()

    def openCreateAccountWindow(self):
        ca = CreateAcc()
        ca.show()
        self.close()

    def checkIfTheFieldsAreFull(self):
        if self.i_email.text() != '' and self.i_password.text() != '':
            return True
        self.lbl_fields.show()
        return False

    def emailAndPassword(self):
        ans = DBConnection.checkLoginData(self.i_email.text(), self.i_password.text())
        if ans == self.i_password.text():
            return True
        self.lbl_incorrect.show()
        return False

    def isUserLogedin(self):
        ans = DBConnection.checkIfAlreadyLogedin(self.i_email.text())
        if ans[0][0] == 0:
            return False
        self.lbl_loged.show()
        return True

    def login(self):
        self.lbl_fields.hide()
        self.lbl_loged.hide()
        self.lbl_incorrect.hide()
        # add all tests , pass login data and change logged in value in DB
        if self.checkIfTheFieldsAreFull() and self.emailAndPassword() and not self.isUserLogedin():
            DBConnection.changeToLoggedIn(str(self.i_email.text()))
            print("logged in", str(self.i_email.text()))
            # creating instance of current_user and open main app
            res = DBConnection.getUser(self.i_email.text())
            current_user = User(*res[0])
            myapp = App(current_user)
            myapp.show()
            self.close()

        else:
            print("failed to login")
