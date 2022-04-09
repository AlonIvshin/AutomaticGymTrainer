from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.uic import loadUi
from Utils import DBConnection


class WatchExerciseInstructions(QtWidgets.QMainWindow):
    def __init__(self, videoId, exercise_id):
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        super().__init__()
        self.ui = loadUi("./ui/instructions.ui", self)
        self.exercise_id = exercise_id
        self.centralwid = QtWidgets.QWidget(self)
        self.vlayout = QtWidgets.QVBoxLayout()
        self.webview = QtWebEngineWidgets.QWebEngineView()
        self.webview.setUrl(QUrl("https://www.youtube.com/embed/" + videoId))
        self.horizontalLayout.addWidget(self.webview)
        # self.show()
        # setting alignment to the text
        # self.lbl_txt.setAlignment(Qt.AlignLeft)
        # making label multi-line
        # self.lbl_txt.setWordWrap(True)
        self.getText()

    def getText(self):
        try:
            print(self.exercise_id)
            theText = DBConnection.getExerciseDescription(self.exercise_id)
            self.lbl_txt.setText(theText)
            self.lbl_txt.show()
        except Exception as error:
            print(error)
