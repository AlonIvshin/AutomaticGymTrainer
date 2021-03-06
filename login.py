from PyQt5.QtWidgets import QDialog, QMainWindow
from PyQt5.uic import loadUi
from createacc import CreateAcc
from Utils import DBConnection
from ClassObjects.User import User
from app import App
from appAdmin import AdminApp
from PyQt5 import QtWidgets



class Login(QDialog):
    def __init__(self, widget):
        super().__init__()
        self.ui = loadUi("./ui/login.ui", self)
        self.setFixedSize(1920, 1000)
        self.i_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.bt_click.clicked.connect(self.openCreateAccountWindow)
        self.bt_login.clicked.connect(self.login)

        self.lblMessage.hide()
        #self.showMaximized()

        self.widget = widget

    def openCreateAccountWindow(self):
        ca = CreateAcc(self.widget)
        self.widget.addWidget(ca)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        ''' Old 
        # ca = CreateAcc()
        # ca.show()
        # self.close()
        
        ca = CreateAcc()
        ca.show()
        self.close()'''

    def checkIfTheFieldsAreFull(self):
        if self.i_email.text() != '' and self.i_password.text() != '':
            return True
        self.lblMessage.setText("Please fill all the fields!")
        self.lblMessage.show()
        return False

    def emailAndPassword(self):
        ans = DBConnection.checkLoginData(self.i_email.text(), self.i_password.text())
        if ans == self.i_password.text():
            return True
        self.lblMessage.setText("Email or password incorrect!")
        self.lblMessage.show()
        return False

    def isUserLogedin(self):
        ans = DBConnection.checkIfAlreadyLogedin(self.i_email.text())
        if ans[0][0] == 0:
            return False
        self.lblMessage.setText("This account is already logged in")
        self.lblMessage.show()
        return True

    def login(self):
        self.lblMessage.hide()
        # add all tests , pass login data and change logged in value in DB
        if self.checkIfTheFieldsAreFull() and self.emailAndPassword() and not self.isUserLogedin():
            DBConnection.changeToLoggedIn(str(self.i_email.text()))
            print("logged in", str(self.i_email.text()))
            # creating instance of current_user and open main app
            res = DBConnection.getUser(self.i_email.text())
            current_user = User(*res[0])
            if current_user.type == 'trainee':
                myapp = App(current_user, self.widget)
                self.widget.addWidget(myapp)
                self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
            elif current_user.type == 'admin':
                myapp = AdminApp(current_user, self.widget)
                self.widget.addWidget(myapp)
                self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
            else:
                print("Login Error")
                exit(1)

            #myapp = App(current_user)
            #myapp.show()
            self.close()

        else:
            print("failed to login")



'''class Login(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        self.ui = loadUi("./ui/login3.ui", self)
        self.setFixedSize(1200, 800)

        self.bt_click.clicked.connect(self.openCreateAccountWindow)
        self.bt_login.clicked.connect(self.login)
        self.lbl_fields.hide()
        self.lbl_loged.hide()
        self.lbl_incorrect.hide()

        self.widget = widget


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
            myapp = App(current_user,self.widget)
            self.widget.addWidget(myapp)
            self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
            #myapp = App(current_user)
            #myapp.show()
            #self.close()

        else:
            print("failed to login")'''
