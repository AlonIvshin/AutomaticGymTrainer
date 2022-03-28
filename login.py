from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("login.ui", self)