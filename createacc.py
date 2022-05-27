from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
import re
from Utils import DBConnection
from PyQt5 import QtWidgets


class CreateAcc(QDialog):
    def __init__(self, widget):
        super().__init__()
        self.ui = loadUi("./ui/createacc.ui", self)
        self.setFixedSize(1920, 1000)
        self.bt_confirm.clicked.connect(self.confirm)
        self.bt_return.clicked.connect(self.returnFromScreen)
        self.i_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.i_password2.setEchoMode(QtWidgets.QLineEdit.Password)

        self.lblMessage.hide()
        self.widget = widget

    def emailTest(self):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email = self.i_email.text()
        if re.fullmatch(regex, email):
            return True
        else:
            self.lblMessage.setText("Invalid Email!")
            self.lblMessage.show()
            return False

    def emailExist(self):
        ans = None
        try:
            email = self.i_email.text()
            ans = DBConnection.isEmailExist(str(email))  # crush
            if ans != 0:
                self.lblMessage.setText("Email address is already exist!")
                self.lblMessage.show()
                return False
            else:
                print("IM HERE")
                return True
        except Exception as error:
            print(error)

    def matchPasswords(self):
        if self.i_password.text() == self.i_password2.text():
            return True
        self.lblMessage.setText('''passwords doesn't match!''')
        self.lblMessage.show()
        return False

    def checkIfTheFieldsAreFull(self):
        if (self.i_email.text() != '' and self.i_password.text() != '' and self.i_password2.text() != ''
                and self.i_firstname.text() != '' and self.i_lastname.text() != '' and self.i_phone.text() != ''):
            return True
        self.lblMessage.setText('''Please fill all the fields!''')
        self.lblMessage.show()
        return False

    def confirm(self):
        self.lblMessage.hide()
        if self.emailTest() and self.emailExist() and self.matchPasswords() and self.checkIfTheFieldsAreFull():
            password = self.i_password.text()
            first = self.i_firstname.text()
            last = self.i_lastname.text()
            email = self.i_email.text()
            phone = self.i_phone.text()
            DBConnection.insertIntoUsers(password, first, last, email, phone)
            self.lblMessage.setText("Registered, press return and login!")
            self.lblMessage.show()

    def returnFromScreen(self):
        self.widget.removeWidget(self.widget.currentWidget())
