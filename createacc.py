from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
import re
from Utils import DBConnection


class CreateAcc(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("./ui/createacc.ui", self)
        self.setFixedSize(1920, 1000)
        self.bt_confirm.clicked.connect(self.confirm)
        self.lbl_bademail.hide()
        self.lbl_badpass.hide()
        self.lbl_notfull.hide()
        self.lbl_bademail2.hide()

    def emailTest(self):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email = self.i_email.text()
        if re.fullmatch(regex, email):
            return True
        else:
            self.lbl_bademail.show()
            return False

    def emailExist(self):
        ans = None
        try:
            email = self.i_email.text()
            ans = DBConnection.isEmailExist(str(email))  # crush
            if ans != 0:
                self.lbl_bademail2.show()
                return False
            else:
                print("IM HERE")
                return True
        except Exception as error:
            print(error)

    def matchPasswords(self):
        if self.i_password.text() == self.i_password2.text():
            return True
        self.lbl_badpass.show()
        return False

    def checkIfTheFieldsAreFull(self):
        if (self.i_email.text() != '' and self.i_password.text() != '' and self.i_password2.text() != ''
                and self.i_firstname.text() != '' and self.i_lastname.text() != '' and self.i_phone.text() != ''):
            return True
        self.lbl_notfull.show()
        return False

    def confirm(self):
        self.lbl_bademail.hide()
        self.lbl_badpass.hide()
        self.lbl_notfull.hide()
        self.lbl_bademail2.hide()
        if self.emailTest() and self.emailExist() and self.matchPasswords() and self.checkIfTheFieldsAreFull():
            print('All Good!')
            password = self.i_password.text()
            first = self.i_firstname.text()
            last = self.i_lastname.text()
            email = self.i_email.text()
            phone = self.i_phone.text()
            DBConnection.insertIntoUsers(password, first, last, email, phone)
