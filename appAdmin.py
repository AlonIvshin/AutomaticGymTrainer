import PyQt5.QtCore as QtCore
import cv2
import mediapipe.python.solutions.pose_connections
from PyQt5.QtCore import QAbstractTableModel, QSortFilterProxyModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QComboBox
from PyQt5.uic import loadUi
from ClassObjects.ExerciseInstruction import ExerciseInstruction
from ClassObjects.Exercise import Exercise
from ClassObjects.Instruction import Instruction
from Utils import DBConnection, WorkoutEstimationFunctions
from mediapipe.python.solutions.pose import PoseLandmark as VertexesEnum


def setAmericanScore(num):
    str = ''
    if int(num) < 55:
        str = 'F'
    if int(num) > 54:
        str = 'E'
    if int(num) > 64:
        str = 'D'
    if int(num) > 74:
        str = 'C'
    if int(num) > 84:
        str = 'B'
    if int(num) > 89:
        str = 'A'
    if int(num) > 94:
        str = 'A+'
    return str


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.table_data = data
        self.header_counter = 0  # ++ happens before using this index in headerData
        self.header_labels = ['']

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.table_data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self.table_data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self.table_data[0])

    # implements the header that will be presented in the table view
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return str(self.header_labels[section])
        return super().headerData(section, orientation, role)

    def setHeaderList(self, headers):
        self.header_labels = headers


class AdminApp(QMainWindow):
    def __init__(self, current_user, widget):
        super().__init__()
        self.exercise = None
        self.ui = loadUi("./ui/appAdmin.ui", self)
        # LOAD TAB WIDGET CSS FILE
        with open('ui/tab2.css', "r") as fh:
            tw = fh.read()
            self.tabWidget.setStyleSheet(tw)
        self.setFixedSize(1920, 1000)
        self.current_user = current_user
        self.tabWidget.setCurrentIndex(0)  # sets default tab
        self.widget = widget

        # Tab #1 - Greetings
        self.lbl_welcome.setText('Welcome ' + current_user.first_name + ' ' + current_user.last_name)  # greeting user

        # Tab #2
        '''
        1. Set functions
        2. Load Tables and set table view
        3. Set labels and exercise id
        '''
        self.bt_addExerciseMngExercises.clicked.connect(self.addExercise)  # Finished
        self.bt_deleteExerciseMngExercises.clicked.connect(self.deleteExercise)  # ToDo
        self.bt_clearFormMngExercises.clicked.connect(self.clearLabelsAndTextMngExercise)  # Finished
        self.bt_saveChangesMngExercises.clicked.connect(self.saveEditedExercise)  # Finished

        self.loadExercisesData()
        self.selected_exercise_id = -1

        self.table_exercisesMngExercises.setColumnHidden(0, True)
        self.table_exercisesMngExercises.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_exercisesMngExercises.clicked.connect(self.manageExerciseTableClicked)
        self.label_messagesMngExercises.hide()

        # Tab #3 - Manage instructions
        self.loadCoordinatesImage()  # load image
        self.initManageInstructionsComboBoxs()  # set combo boxes

        self.bt_addInstructionMngInstructions.clicked.connect(self.addInstruction)  # Finished
        self.bt_deleteInstructionMngInstructions.clicked.connect(self.deleteInstructionMngInstructions)
        self.bt_clearInstructionMngInstructions.clicked.connect(self.clearLabelsAndTextMngInstructions)  # Finished
        self.bt_saveInstructionMngInstructions.clicked.connect(self.saveEditedInstruction)  # Finished

        self.loadInstructionsData()
        self.selected_instruction_id = -1

        self.table_instructionsMngInstructions.setColumnHidden(0, True)
        self.table_instructionsMngInstructions.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_instructionsMngInstructions.clicked.connect(self.manageInstructionsTableClicked)
        self.label_messagesMngInstructions.hide()

        # Tab #4 - Edit exercises (instructions)
        # image loaded with loadCoordinates function - no need to recall
        self.loadExerciseToComboBoxExerciseInstructions()
        self.comboBox_selectExerciseMngExerciseInstructions.currentIndexChanged.connect(
            self.mngExerciseInstructionExerciseSelected)


        self.loadInstructionsDataForExerciseInstructionTab()  # for

        self.loadDevTriggerToComboBoxExerciseInstructions()
        self.comboBox_alertDevTriggerMngExerciseInstructions.currentIndexChanged.connect(
            self.mngExerciseInstructionAlertDevTriggerSelected)

        self.loadInstructionTypeToComboBoxExerciseInstructions()
        self.comboBox_instructionTypeMngExerciseInstructions.currentIndexChanged.connect(
            self.mngExerciseInstructionInstructionTypeSelected)

        self.table_instructionsMngExerciseInstructions.setColumnHidden(0, True)
        self.table_instructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table_instructionsMngExerciseInstructions.setColumnWidth(1, 100)
        self.table_instructionsMngExerciseInstructions.setColumnWidth(2, 100)
        self.table_instructionsMngExerciseInstructions.setColumnWidth(3, 100)
        self.table_instructionsMngExerciseInstructions.setColumnWidth(4, 50)
        self.table_instructionsMngExerciseInstructions.setColumnWidth(6, 50)

        self.table_instructionsMngExerciseInstructions.clicked.connect(
            self.manageInstructionTableClickedMngExerciseInstruction)
        self.table_AlertsMngExerciseInstructions.clicked.connect(
            self.manageAlertTableClickedMngExerciseInstruction)  # set alert Id for later uses (such as add e. instruction)
        self.table_extendedAlertsMngExerciseInstructions.clicked.connect(
            self.manageExtendedAlertTableClickedMngExerciseInstruction)  # set extended alert id for later uses

        self.selected_instruction_id_MngExerciseInstruction = -1  # Set indexes for selected rows in tables
        self.selected_alert_id_MngExerciseInstruction = -1

        self.bt_addExerciseInstructionMngExerciseInstructions.clicked.connect(
            self.addExerciseInsturctionMngExerciseInstruction)

        self.bt_deleteExerciseInstructionMngExerciseInstructions.clicked.connect(
            self.deleteExerciseInstructionMngExerciseInstruction)


        # self.table_instructionsMngExerciseInstructions.clicked.connect(self.manageInstructionsTableClicked)
        self.label_selectedAlertMngExerciseInstructions.hide()
        self.label_selectedExtendedAlertMngExerciseInstructions.hide()
        self.label_msgMngExerciseInstructions.hide()


        # Tab #5 - Mange Alerts
        self.loadInstructionsDataForAlerts()
        self.tb_instructionsMngAlerts.setColumnHidden(0, True)
        self.tb_instructionsMngAlerts.clicked.connect(self.instructionsAlertsTablePressed)
        self.tb_instructionsMngAlerts.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.tb_alertsMngAlerts.clicked.connect(self.alertsTablePressed)
        self.bt_clearFormMngAlerts.clicked.connect(self.clearLabelsAndTextMngAlerts)
        self.bt_addAlertMngAlerts.clicked.connect(self.addAlert)
        self.selected_instructionAlerts_id = -1
        self.selected_alert_id = -1
        self.bt_deleteAlertMngAlerts.clicked.connect(self.deleteAlert)
        self.bt_updateAlertMngAlerts.clicked.connect(self.updateAlert)

    # Tab4
    def ClearLabelsMngExerciseInstructions(self):
        self.label_selectedAlertMngExerciseInstructions.setText("")
        self.label_selectedExtendedAlertMngExerciseInstructions.setText("")
        self.label_msgMngExerciseInstructions.setText("")

    # Load image to Tab #2
    # Load posture image for who needes it
    def loadCoordinatesImage(self):
        vertexes_image_url = 'https://i.imgur.com/C5eBW20.png'
        vertexes_image = WorkoutEstimationFunctions.getImageFromLink(vertexes_image_url)
        vertexes_image = cv2.resize(vertexes_image, (528, 300))
        vertexes_image = cv2.cvtColor(vertexes_image, cv2.COLOR_BGR2RGB)
        vertexes_image = QImage(vertexes_image,
                                vertexes_image.shape[1],
                                vertexes_image.shape[0], QImage.Format_RGB888)
        self.label_bodykeypointsMngInstructions.setPixmap(QPixmap.fromImage(vertexes_image))  # For tab #3
        self.label_bodykeypointsMngExerciseInstructions.setPixmap(QPixmap.fromImage(vertexes_image))  # For tab #4
        self.label_bodykeypointsMngInstructions.show()
        self.label_bodykeypointsMngExerciseInstructions.show()

    def loadExercisesData(self):
        headers = ['', 'Exercise Name', 'Main body part']
        self.exerciseData = DBConnection.getExerciesNamesAndTarget()
        self.exerciseData = sorted(self.exerciseData, key=lambda x: x[1])  # Sort data by exercise name
        self.exerciseModel = TableModel(self.exerciseData)
        self.exerciseModel.setHeaderList(headers)
        self.exercise_proxy_model = QSortFilterProxyModel()
        self.exercise_proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.exercise_proxy_model.setSourceModel(self.exerciseModel)
        self.exercise_proxy_model.sort(0, Qt.AscendingOrder)
        self.table_exercisesMngExercises.setModel(self.exercise_proxy_model)
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        self.lineEdit_searchBarMngExercises.textChanged.connect(self.exercise_proxy_model.setFilterFixedString)

    def manageInstructionTableClickedMngExerciseInstruction(self):
        self.ClearLabelsMngExerciseInstructions()
        index = self.table_instructionsMngExerciseInstructions.currentIndex()
        newIndex = self.table_instructionsMngExerciseInstructions.model().index(index.row(), 0)
        newIndex2 = self.table_instructionsMngExerciseInstructions.model().index(index.row(), 1)

        self.selectedInstructionExerciseInstruction = self.table_instructionsMngExerciseInstructions.model().data(
            newIndex)  # contains the index of the selected instruction

        self.selected_instruction_id_MngExerciseInstruction = self.selectedInstructionExerciseInstruction  # save selected instruction id for later uses (such as add)
        self.label_selectedInstructionMngExerciseInstructions.setText(
            f"Selected instruction {self.selected_instruction_id_MngExerciseInstruction}")
        '''txt = self.table_instructionsMngExerciseInstructions.model().data(newIndex2)
        self.label_messagesMngExercises.setText(txt + " is chosen")
        self.label_messagesMngExercises.show()'''
        '''self.loadExerciseToScreenFields()'''
        self.selected_alert_id_MngExerciseInstruction = -1  # reset selected alert id
        self.selected_extended_id_MngExerciseInstruction = -1  # reset selected alert id
        self.label_selectedAlertMngExerciseInstructions.setText("")
        self.loadAlertsForSelectedInstruction(self.table_AlertsMngExerciseInstructions)
        self.loadExtendedAlertsForSelectedInstruction(self.table_extendedAlertsMngExerciseInstructions)


    # for tab 3
    def deleteInstructionMngInstructions(self):
        if self.selected_instruction_id == -1:
            self.label_messagesMngInstructions.setText("Please select instruction before deleting")
            self.label_messagesMngInstructions.show()
            return
        res = DBConnection.getAlertsForInstruction(self.selected_instruction_id)
        if res:
            self.label_messagesMngInstructions.setText("Delete all alerts before deleting the instruction")
            self.label_messagesMngInstructions.show()
            return
        res = DBConnection.getExerciseInstructionsForInstruction(self.selected_instruction_id)
        if res:
            self.label_messagesMngInstructions.setText("Delete all exercise instructions before deleting the instruction")
            self.label_messagesMngInstructions.show()
            return
        res = DBConnection.deleteInstruction(self.selected_instruction_id)
        if res:
            self.label_messagesMngInstructions.setText("Instruction deleted")
            self.label_messagesMngInstructions.show()

            self.initManageInstructionsComboBoxs()
            self.loadInstructionsData()
            self.selected_instruction_id = -1

    # For first table in tab #4 - Edit exercise
    def loadInstructionsDataForExerciseInstructionTab(self):
        self.ClearLabelsMngExerciseInstructions()  # Hide labels
        headers = ['', 'Vertex1', 'Vertex2', 'Vertex3', 'Angle', 'Description', 'Axis']
        self.instructionsMngExerciseInstructionsData = DBConnection.getAllInstructions()
        self.instructionsMngExerciseInstructionsData = sorted(self.instructionsMngExerciseInstructionsData,
                                                              key=lambda x: x[0])  # Sort data by instruction id
        self.instructionsMngExerciseInstructionsModel = TableModel(self.instructionsMngExerciseInstructionsData)
        self.instructionsMngExerciseInstructionsModel.setHeaderList(headers)
        self.instructionMngExerciseInstruction_proxy_model = QSortFilterProxyModel()
        self.instructionMngExerciseInstruction_proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.instructionMngExerciseInstruction_proxy_model.setSourceModel(self.instructionsMngExerciseInstructionsModel)
        self.instructionMngExerciseInstruction_proxy_model.sort(0, Qt.AscendingOrder)
        self.table_instructionsMngExerciseInstructions.setModel(self.instructionMngExerciseInstruction_proxy_model)
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        self.lineEdit_searchBarInstructionManageExerciseInstructions.textChanged.connect(
            self.instructionMngExerciseInstruction_proxy_model.setFilterFixedString)
        '''lineEdit_searchBarExerciseInstructionBarManageExerciseInstructions'''

        # set instruction mng clicked action
        #self.table_instructionsMngExerciseInstructions.clicked.connect(self.InstructionSelected)

    # For alerts table in tab  #4 - Edit exercise
    def loadAlertsForSelectedInstruction(self, table):
        headers = ['', '', 'Text', 'Link']
        self.alertsDataMngExerciseInstructions = DBConnection.getAlertsOfInstruction(
            self.selectedInstructionExerciseInstruction)
        '''if self.alertsDataMngExerciseInstructions == []:
            self.alertsDataMngExerciseInstructions = [""]'''

        self.alertsDataMngExerciseInstructions = sorted(self.alertsDataMngExerciseInstructions,
                                                        key=lambda x: x[0])  # Sort data by instruction id
        if self.alertsDataMngExerciseInstructions == []:
            self.alertsDataMngExerciseInstructions = [""]
        self.alertsModelMngExerciseInstructions = TableModel(self.alertsDataMngExerciseInstructions)
        self.alertsModelMngExerciseInstructions.setHeaderList(headers)
        self.alertsMngExerciseInstructions_proxy_model = QSortFilterProxyModel()
        self.alertsMngExerciseInstructions_proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.alertsMngExerciseInstructions_proxy_model.setSourceModel(self.alertsModelMngExerciseInstructions)
        self.alertsMngExerciseInstructions_proxy_model.sort(0, Qt.AscendingOrder)
        table.setModel(self.alertsMngExerciseInstructions_proxy_model)
        self.lineEdit_searchBarAlertsManageExerciseInstructions.textChanged.connect(
            self.alertsMngExerciseInstructions_proxy_model.setFilterFixedString)

        if self.alertsDataMngExerciseInstructions == [""]:
            return

        table.setColumnHidden(0, True)
        table.setColumnHidden(1, True)

        self.table_AlertsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_AlertsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

    # For extended alerts table in tab #4 - Edit exercise
    def loadExtendedAlertsForSelectedInstruction(self, table):
        headers = ['', '', 'Text', 'Link']
        #self.alertsDataMngExerciseInstructions = DBConnection.getAlertsOfInstruction(
         #   self.selectedInstructionExerciseInstruction)
        row_index = self.table_instructionsMngExerciseInstructions.currentIndex()
        vertex1_index = self.table_instructionsMngExerciseInstructions.model().index(row_index.row(), 1)
        vertex2_index = self.table_instructionsMngExerciseInstructions.model().index(row_index.row(), 2)
        vertex3_index = self.table_instructionsMngExerciseInstructions.model().index(row_index.row(), 3)

        vertex1 = self.table_instructionsMngExerciseInstructions.model().data(vertex1_index)
        vertex2 = self.table_instructionsMngExerciseInstructions.model().data(vertex2_index)
        vertex3 = self.table_instructionsMngExerciseInstructions.model().data(vertex3_index)

        self.ExtendedAlertsDataMngExerciseInstructions = DBConnection.getAllAlertsFor3Vertices(vertex1,vertex2,vertex3)
        '''if self.alertsDataMngExerciseInstructions == []:
            self.alertsDataMngExerciseInstructions = [""]'''

        self.ExtendedAlertsDataMngExerciseInstructions = sorted(self.ExtendedAlertsDataMngExerciseInstructions,
                                                        key=lambda x: x[0])  # Sort data by instruction id

        if self.ExtendedAlertsDataMngExerciseInstructions == []:
            self.ExtendedAlertsDataMngExerciseInstructions = [""]
        self.ExtendedAlertsModelMngExerciseInstructions = TableModel(self.ExtendedAlertsDataMngExerciseInstructions)
        self.ExtendedAlertsModelMngExerciseInstructions.setHeaderList(headers)
        self.ExtendedAlertsMngExerciseInstructions_proxy_model = QSortFilterProxyModel()
        self.ExtendedAlertsMngExerciseInstructions_proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.ExtendedAlertsMngExerciseInstructions_proxy_model.setSourceModel(self.ExtendedAlertsModelMngExerciseInstructions)
        self.ExtendedAlertsMngExerciseInstructions_proxy_model.sort(0, Qt.AscendingOrder)
        table.setModel(self.ExtendedAlertsMngExerciseInstructions_proxy_model)
        '''self.lineEdit_searchBarAlertsManageExerciseInstructions.textChanged.connect(
            self.alertsMngExerciseInstructions_proxy_model.setFilterFixedString)'''


        if self.ExtendedAlertsDataMngExerciseInstructions == [""]:
            return

        table.setColumnHidden(0, True)
        table.setColumnHidden(1, True)

        self.table_extendedAlertsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_extendedAlertsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

    # tab  # 4 - Edit exercise
    def manageAlertTableClickedMngExerciseInstruction(self):
        index = self.table_AlertsMngExerciseInstructions.currentIndex()
        newIndex = self.table_AlertsMngExerciseInstructions.model().index(index.row(), 0)
        newIndex2 = self.table_AlertsMngExerciseInstructions.model().index(index.row(), 1)

        self.selectedAlertExerciseInstruction = self.table_AlertsMngExerciseInstructions.model().data(
            newIndex)  # contains the index of the selected instruction

        self.selected_alert_id_MngExerciseInstruction = self.selectedAlertExerciseInstruction  # save selected instruction id for later uses (such as add)
        self.label_selectedAlertMngExerciseInstructions.setText(
            f"Selected alert {self.selected_alert_id_MngExerciseInstruction}")
        self.label_selectedAlertMngExerciseInstructions.show()

    # tab  # 4
    def manageExtendedAlertTableClickedMngExerciseInstruction(self):
        index = self.table_extendedAlertsMngExerciseInstructions.currentIndex()
        newIndex = self.table_extendedAlertsMngExerciseInstructions.model().index(index.row(), 0)
        newIndex2 = self.table_extendedAlertsMngExerciseInstructions.model().index(index.row(), 1)

        self.selectedExtendedAlertExerciseInstruction = self.table_extendedAlertsMngExerciseInstructions.model().data(
            newIndex)  # contains the index of the selected instruction

        self.selected_extended_alert_id_MngExerciseInstruction = self.selectedExtendedAlertExerciseInstruction  # save selected instruction id for later uses (such as add)
        self.label_selectedExtendedAlertMngExerciseInstructions.setText(
            f"Selected extended alert {self.selected_extended_alert_id_MngExerciseInstruction}")
        self.label_selectedExtendedAlertMngExerciseInstructions.show()

    # TAB 4 - Loads trigger types into the combo box
    def loadDevTriggerToComboBoxExerciseInstructions(self):
        self.selected_trigger_id_MngExerciseInstructions = -1
        self.comboBox_alertDevTriggerMngExerciseInstructions.addItem("Select trigger")
        for item in ['Both', 'Negative', 'Positive']:
            self.comboBox_alertDevTriggerMngExerciseInstructions.addItem(item)

    # TAB 4 - Loads instruction types into the combo box
    def loadInstructionTypeToComboBoxExerciseInstructions(self):
        self.selected_instruction_type_id_MngExerciseInstructions = -1
        self.comboBox_instructionTypeMngExerciseInstructions.addItem("Select instruction type")
        for item in ['Dynamic', 'Static']:
            self.comboBox_instructionTypeMngExerciseInstructions.addItem(item)

    # tab  # 4 - Edit exercise
    def loadExerciseToComboBoxExerciseInstructions(self):
        self.ExerciseInstructionsExerciseComboBoxData = res = DBConnection.getExerciesNamesAndTarget()
        self.selected_exercise_id_MngExerciseInstructions = -1
        self.comboBox_selectExerciseMngExerciseInstructions.addItem("Select exercise")
        for item in res:
            self.comboBox_selectExerciseMngExerciseInstructions.addItem(item[1])

    # tab  # 4
    def mngExerciseInstructionExerciseSelected(self, index):
        """ Need to load to combo box """
        '''comboBox_selectExerciseMngExerciseInstructions'''
        '''table_ExerciseInstructionsMngExerciseInstructions'''

        ''' need to get exercise from combo box index'''
        if index == 0:
            return
        self.selected_exercise_id_MngExerciseInstructions = self.ExerciseInstructionsExerciseComboBoxData[index - 1][
            0]  # index -1 = initial index is select exercise
        self.loadExerciseInstructionsForSelectedExercise(
            self.selected_exercise_id_MngExerciseInstructions)  # load instructions

    # tab  # 4
    def mngExerciseInstructionAlertDevTriggerSelected(self, index):
        self.selected_trigger_id_MngExerciseInstructions = index - 1
        print("trigger " + str(self.selected_trigger_id_MngExerciseInstructions))

    # tab  # 4
    def mngExerciseInstructionInstructionTypeSelected(self, index):
        self.selected_instruction_type_id_MngExerciseInstructions = index - 1
        print("type  " + str(self.selected_instruction_type_id_MngExerciseInstructions))

    # tab  # 4 - Edit exercise
    def setLabelsForMngExerciseInstructions(self):
        pass

    # tab  # 4 - Edit exercise
    def loadExerciseInstructionsForSelectedExercise(self, exercise_id):
        ''' sort by instruction id '''
        '''headers = ['Instruction ID', 'Alert text', 'Alert image', 'Positive deviation', 'Negative deviation', 'Stage',
                   'Type', 'Trigger', 'Extended Id trigger']  # For alert text and alert image'''

        headers = ['Instruction ID', 'Alert ID', 'Positive deviation', 'Negative deviation', 'Stage',
                   'Type', 'Trigger', 'Extended Id trigger']  # For alert ID
        self.ExerciseInstructionMngExerciseInstructionData = DBConnection.getAllExerciseInstructionData(
            exerciseId=exercise_id)

        if self.ExerciseInstructionMngExerciseInstructionData == []:
            return
        self.ExerciseInstructionMngExerciseInstructionData = sorted(self.ExerciseInstructionMngExerciseInstructionData,
                                                                    key=lambda x: x[2])  # Sort data by instruction id

        self.ExerciseInstructionMngExerciseInstructionAlertsData = DBConnection.getAllAlertsData(exercise_id)
        self.ExerciseInstructionMngExerciseInstructionAlertsData = sorted(
            self.ExerciseInstructionMngExerciseInstructionAlertsData,
            key=lambda x: x[1])  # Sort data by instruction id

        self.ExerciseInstructionsWithAlertsMngExerciseInstruction = []
        for index in range(len(self.ExerciseInstructionMngExerciseInstructionData)):
            '''instruction_id, alert_id \ (alert text + alert image),pos dev,neg dev,stage,type,trigger,ex id??'''
            ''' what about alert extended id'''
            current_exe_ins = self.ExerciseInstructionMngExerciseInstructionData[index]
            current_exe_ins_alert = self.ExerciseInstructionMngExerciseInstructionAlertsData[index]
            '''self.ExerciseInstructionMngExerciseInstructionAlertsData[
                current_exe_ins[2] - 1]'''  # this will get id and subtract 1 (list index starts from zero)
            ins_id = current_exe_ins[1]
            alert_id = current_exe_ins_alert[0]  # for alert id
            # alert_text = current_exe_ins_alert[2]
            # alert_img_link = current_exe_ins_alert[3]
            alert_pos_dev = current_exe_ins[3]
            alert_pos_neg = current_exe_ins[4]
            stage = current_exe_ins[5]
            type = current_exe_ins[6]
            trigger = current_exe_ins[7]
            extended_id = current_exe_ins[8]
            '''to_add = [ins_id, alert_text, alert_img_link, alert_pos_dev, alert_pos_neg, stage, type, trigger,
                      extended_id]'''  # for alert image and alert text
            to_add = [ins_id, alert_id, alert_pos_dev, alert_pos_neg, stage, type, trigger,
                      extended_id]  # for alert id
            to_add = tuple(to_add)
            self.ExerciseInstructionsWithAlertsMngExerciseInstruction.append(to_add)

        # if no exercise instructions exist
        if self.ExerciseInstructionsWithAlertsMngExerciseInstruction == []:
            self.ExerciseInstructionsWithAlertsMngExerciseInstruction = ['']

        self.ExerciseInstructionsWithAlertsMngExerciseInstructionsModel = TableModel(
            self.ExerciseInstructionsWithAlertsMngExerciseInstruction)
        self.ExerciseInstructionsWithAlertsMngExerciseInstructionsModel.setHeaderList(headers)
        self.ExerciseInstructionWithAlertsMngExerciseInstruction_proxy_model = QSortFilterProxyModel()
        self.ExerciseInstructionWithAlertsMngExerciseInstruction_proxy_model.setFilterKeyColumn(
            -1)  # Search all columns.
        self.ExerciseInstructionWithAlertsMngExerciseInstruction_proxy_model.setSourceModel(
            self.ExerciseInstructionsWithAlertsMngExerciseInstructionsModel)
        self.ExerciseInstructionWithAlertsMngExerciseInstruction_proxy_model.sort(0, Qt.AscendingOrder)
        self.table_ExerciseInstructionsMngExerciseInstructions.setModel(
            self.ExerciseInstructionWithAlertsMngExerciseInstruction_proxy_model)
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        self.lineEdit_searchBarExerciseInstructionBarManageExerciseInstructions.textChanged.connect(
            self.ExerciseInstructionWithAlertsMngExerciseInstruction_proxy_model.setFilterFixedString)

        self.table_ExerciseInstructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_ExerciseInstructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_ExerciseInstructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_ExerciseInstructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_ExerciseInstructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table_ExerciseInstructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table_ExerciseInstructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.table_ExerciseInstructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(7,QHeaderView.Stretch)
        self.table_ExerciseInstructionsMngExerciseInstructions.clicked.connect(self.ExerciseInstructionClickedMngExerciseInstructions)



        '''self.table_ExerciseInstructionsMngExerciseInstructions.setColumnHidden(0, True)
        self.table_ExerciseInstructionsMngExerciseInstructions.horizontalHeader().setSectionResizeMode(1,
                                                                                                       QHeaderView.Stretch)'''
    def ExerciseInstructionClickedMngExerciseInstructions(self):
        index = self.table_ExerciseInstructionsMngExerciseInstructions.currentIndex()
        self.selected_exercise_instruction_id_MngExerciseInstructions = self.ExerciseInstructionMngExerciseInstructionData[index.row()][0]
        self.label_msgMngExerciseInstructions.setText(f"Selected exercise instruction {self.selected_exercise_instruction_id_MngExerciseInstructions}")
        self.label_msgMngExerciseInstructions.show()


    # tab  # 4 - Add exercise instructions
    def addExerciseInsturctionMngExerciseInstruction(self):
        ins_id = self.selected_instruction_id_MngExerciseInstruction
        alert_id = self.selected_alert_id_MngExerciseInstruction
        if self.checkFilledAreFullMngExerciseInstructions():
            self.label_msgMngExerciseInstructions.setText("Please fill all the fields")
            self.label_msgMngExerciseInstructions.show()
            return
        pos_dev = self.lineEdit_posDevMngExerciseInstructions.text()
        neg_dev = self.lineEdit_negDevMngExerciseInstructions.text()
        stage = self.lineEdit_stageMngExerciseInstructions.text()
        ex_ins_type = self.comboBox_instructionTypeMngExerciseInstructions.currentText()
        ex_ins_trigger = self.comboBox_alertDevTriggerMngExerciseInstructions.currentText()
        exe_ins_extended_id = self.selected_extended_alert_id_MngExerciseInstruction
        '''
        extended ID reasons:
        when a trainee does a movement that exceeds upper case of movment - exmaple: 
        moving the hand towards the ceiling - the correct range is (example) 90->150, 
        the trainee moves the hand until 175 - not good
        '''

        '''
        both holds id in combo box
        currentText
        selected_trigger_id_MngExerciseInstructions 
        selected_instruction_type_id_MngExerciseInstructions
        '''
        # -1 -> creates new exercise instruction
        exe_ins = ExerciseInstruction(-1, self.selected_exercise_id_MngExerciseInstructions, ins_id, alert_id, pos_dev,
                                      neg_dev, stage, ex_ins_type, ex_ins_trigger, exe_ins_extended_id)
        res = DBConnection.addNewExerciseInstruction(exe_ins)

        ''' Don't forget to reload the table after this line '''
        ''' Don't forget to reload the table after this line '''
        ''' Don't forget to reload the table after this line '''
        ''' Don't forget to reload the table after this line '''
        ''' Don't forget to reload the table after this line '''

        # exercise id
        self.loadExerciseInstructionsForSelectedExercise(self.selected_exercise_id_MngExerciseInstructions)

    # tab  # 4 - delete exercise instructions
    def deleteExerciseInstructionMngExerciseInstruction(self):
        #self.selected_exercise_instruction_id_MngExerciseInstructions - holds exercise instruction id
        if self.selected_exercise_instruction_id_MngExerciseInstructions == -1:
            self.label_msgMngExerciseInstructions.setText("Please choose exercise instruction")
            self.label_msgMngExerciseInstructions.show()
            return
        res = DBConnection.deleteExerciseInsturction(self.selected_exercise_instruction_id_MngExerciseInstructions)
        if res:
            self.label_msgMngExerciseInstructions.setText("exercise instruction deleted")
            self.label_msgMngExerciseInstructions.show()
            self.loadExerciseInstructionsForSelectedExercise(self.selected_exercise_id_MngExerciseInstructions)




        pass

    # tab  # 4 - Edit exercise
    def checkFilledAreFullMngExerciseInstructions(self):
        return self.lineEdit_posDevMngExerciseInstructions.text() == '' or \
               self.lineEdit_negDevMngExerciseInstructions.text() == '' or \
               self.lineEdit_stageMngExerciseInstructions.text() == '' or \
               self.selected_trigger_id_MngExerciseInstructions < 0 or \
               self.selected_instruction_type_id_MngExerciseInstructions < 0

    def loadInstructionsData(self):
        headers = ['', 'Vertex1', 'Vertex2', 'Vertex3', 'Angle', 'Description', 'Axis']
        self.instructionData = DBConnection.getAllInstructions()
        self.instructionData = sorted(self.instructionData, key=lambda x: x[0])  # Sort data by instruction id
        self.instructionModel = TableModel(self.instructionData)
        self.instructionModel.setHeaderList(headers)
        self.instruction_proxy_model = QSortFilterProxyModel()
        self.instruction_proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.instruction_proxy_model.setSourceModel(self.instructionModel)
        self.instruction_proxy_model.sort(0, Qt.AscendingOrder)
        self.table_instructionsMngInstructions.setModel(self.instruction_proxy_model)
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        self.lineEdit_searchBarManageInstructions.textChanged.connect(self.instruction_proxy_model.setFilterFixedString)

    def clearLabelsAndTextMngExercise(self):
        self.lineEdit_enameMngExercises.setText('')
        self.plainTextEdit_descriptionMngExercises.clear()
        self.lineEdit_stagenumMngExercises.setText('')
        self.lineEdit_videolinkMngExercises.setText('')
        self.lineEdit_mainTargetMngExercises.setText('')
        self.label_messagesMngExercises.setText('')
        self.selected_exercise_id = -1

    def clearLabelsAndTextMngInstructions(self):
        self.lineEdit_angleMngInstructions.setText('')
        self.plainTextEdit_descriptionMngInstructions.clear()
        # How to set default value for combo box
        self.comboBox_vertex1MngInstructions.setCurrentIndex(0)
        self.comboBox_vertex2MngInstructions.setCurrentIndex(0)
        self.comboBox_vertex3MngInstructions.setCurrentIndex(0)
        self.comboBox_axisMngInstructions.setCurrentIndex(0)
        self.label_messagesMngInstructions.setText('')
        self.selected_instruction_id = -1

    # Check if there are any empty fields
    def checkEmptyFieldMngExercise(self):
        return self.lineEdit_enameMngExercises.text() == '' or self.lineEdit_videolinkMngExercises.text() == '' or self.plainTextEdit_descriptionMngExercises.toPlainText() == '' or self.lineEdit_stagenumMngExercises.text() == '' or self.lineEdit_mainTargetMngExercises.text() == ''

    def checkEmptyFieldMngInstruction(self):
        return self.lineEdit_angleMngInstructions.text() == '' or self.plainTextEdit_descriptionMngInstructions.toPlainText() == ''

    # Save changes done with edit exercise
    def saveEditedExercise(self):
        if self.selected_exercise_id == -1:
            self.label_messagesMngExercises.setText("Please choose exercise")
            self.label_messagesMngExercises.show()
            return
        maxCurrentStage = DBConnection.getMaxStageInExercise(self.selected_exercise_id)
        if self.checkEmptyFieldMngExercise():
            self.label_messagesMngExercises.setText("Make sure all fields are filled")
        elif self.selected_exercise_id < maxCurrentStage:
            self.label_messagesMngExercises.setText(f"Existing instruction has stage number of {maxCurrentStage}!")
        else:
            exercise = Exercise(self.selected_exercise_id, self.lineEdit_enameMngExercises.text(),
                                self.lineEdit_videolinkMngExercises.text(),
                                self.plainTextEdit_descriptionMngExercises.toPlainText(),
                                self.lineEdit_stagenumMngExercises.text()
                                , self.lineEdit_mainTargetMngExercises.text())
            self.exercise = exercise
            res = DBConnection.modifyExercise(exercise)
            self.label_messagesMngExercises.setText("Exercise updated")
            self.label_messagesMngExercises.show()
            self.loadExercisesData()

    def saveEditedInstruction(self):
        if self.selected_instruction_id == -1:
            self.label_messagesMngInstructions.setText("Please choose instruction")
            self.label_messagesMngInstructions.show()
            return
        if self.checkEmptyFieldMngInstruction():
            self.label_messagesMngInstructions.setText("Make sure all fields are filled")

        vertex1 = VertexesEnum(self.comboBox_vertex1MngInstructions.currentIndex()).name
        vertex2 = VertexesEnum(self.comboBox_vertex2MngInstructions.currentIndex()).name
        vertex3 = VertexesEnum(self.comboBox_vertex3MngInstructions.currentIndex()).name

        instruction = Instruction(self.selected_instruction_id, vertex1, vertex2, vertex3,
                                  self.lineEdit_angleMngInstructions.text()
                                  , self.plainTextEdit_descriptionMngInstructions.toPlainText(),
                                  str(self.comboBox_axisMngInstructions.currentText()))

        if DBConnection.checkIfInstructionExist(instruction=instruction):
            self.label_messagesMngInstructions.setText("Instruction already exist")
            self.label_messagesMngInstructions.show()
            return
        else:
            self.instruction = instruction
            res = DBConnection.modifyExercise(instruction)
            self.loadInstructionsData()
            self.label_messagesMngInstructions.setText("Instruction updated")
            self.label_messagesMngInstructions.show()

    def loadExerciseToScreenFields(self):
        '''if self.selected_exercise_id == -1:
            self.label_messagesMngExercises.setText("Please choose exercise")
            self.label_messagesMngExercises.show()
        else:
        ^ Might be useless ^
        '''

        res = DBConnection.getExercise(self.selected_exercise_id)
        self.exercise = Exercise(*res[0])
        exercise = self.exercise
        self.lineEdit_enameMngExercises.setText(str(exercise.exercise_name))
        self.plainTextEdit_descriptionMngExercises.setPlainText(str(exercise.description))
        self.lineEdit_stagenumMngExercises.setText(str(exercise.num_of_stages))
        self.lineEdit_videolinkMngExercises.setText(str(exercise.video))
        self.lineEdit_mainTargetMngExercises.setText(str(exercise.main_target))

    def loadInstructionsToScreenFields(self):
        '''if self.selected_instruction_id == -1:
            self.label_messagesMngInstructions.setText("Please choose exercise")
            self.label_messagesMngExercises.show()
        else:
        ^ Might be useless ^
        '''
        res = DBConnection.getInstruction(self.selected_instruction_id)
        self.instruction = Instruction(*res[0])
        instruction = self.instruction

        # Set combo boxes
        pose_index = VertexesEnum[instruction.vertex1].value
        index = self.comboBox_vertex1MngInstructions.findText(instruction.vertex1 + f" {pose_index}",
                                                              Qt.MatchFixedString)
        if index >= 0:
            self.comboBox_vertex1MngInstructions.setCurrentIndex(index)

        pose_index = VertexesEnum[instruction.vertex2].value
        index = self.comboBox_vertex2MngInstructions.findText(instruction.vertex2 + f" {pose_index}",
                                                              Qt.MatchFixedString)
        if index >= 0:
            self.comboBox_vertex2MngInstructions.setCurrentIndex(index)

        pose_index = VertexesEnum[instruction.vertex3].value
        index = self.comboBox_vertex3MngInstructions.findText(instruction.vertex3 + f" {pose_index}",
                                                              Qt.MatchFixedString)
        if index >= 0:
            self.comboBox_vertex3MngInstructions.setCurrentIndex(index)

        index = self.comboBox_axisMngInstructions.findText(instruction.instructionAxis, Qt.MatchFixedString)
        if index >= 0:
            self.comboBox_axisMngInstructions.setCurrentIndex(index)

        self.lineEdit_angleMngInstructions.setText(str(instruction.angle))
        self.plainTextEdit_descriptionMngInstructions.setPlainText(str(instruction.description))

    def addExercise(self):
        if self.checkEmptyFieldMngExercise():
            self.label_messagesMngExercises.setText("Make sure all fields are filled")
            self.label_messagesMngExercises.show()
            return
        exercise = Exercise(-1, self.lineEdit_enameMngExercises.text(), self.lineEdit_videolinkMngExercises.text(),
                            self.plainTextEdit_descriptionMngExercises.toPlainText(),
                            self.lineEdit_stagenumMngExercises.text()
                            , self.lineEdit_mainTargetMngExercises.text())
        res = DBConnection.addNewExercise(exercise)
        if res:
            self.label_messagesMngExercises.setText("Exercise added")
            self.label_messagesMngExercises.show()
            self.loadExercisesData()

    def addInstruction(self):
        if self.checkEmptyFieldMngInstruction():
            self.label_messagesMngExercises.setText("Make sure all fields are filled")
            self.label_messagesMngExercises.show()
            return
        vertex1 = VertexesEnum(self.comboBox_vertex1MngInstructions.currentIndex()).name
        vertex2 = VertexesEnum(self.comboBox_vertex2MngInstructions.currentIndex()).name
        vertex3 = VertexesEnum(self.comboBox_vertex3MngInstructions.currentIndex()).name

        instruction = Instruction(-1, vertex1, vertex2, vertex3, self.lineEdit_angleMngInstructions.text()
                                  , self.plainTextEdit_descriptionMngInstructions.toPlainText(),
                                  str(self.comboBox_axisMngInstructions.currentText()))
        res = DBConnection.addNewInstruction(instruction)
        if res:
            self.label_messagesMngInstructions.setText("Instruction added")
            self.label_messagesMngInstructions.show()
            self.loadInstructionsData()

    def deleteExercise(self):
        pass

    def deleteInstruction(self):
        pass

    # load data when exercise table is clicked
    def manageExerciseTableClicked(self):
        index = self.table_exercisesMngExercises.currentIndex()
        newIndex = self.table_exercisesMngExercises.model().index(index.row(), 0)
        newIndex2 = self.table_exercisesMngExercises.model().index(index.row(), 1)

        self.selected_exercise_id = self.table_exercisesMngExercises.model().data(
            newIndex)  # we can pass eid to the model
        txt = self.table_exercisesMngExercises.model().data(newIndex2)
        self.label_messagesMngExercises.setText(txt + " is chosen")
        self.label_messagesMngExercises.show()

        self.loadExerciseToScreenFields()

    # load data when instruction table is clicked
    # Change row index when clicked on table
    def manageInstructionsTableClicked(self):
        index = self.table_instructionsMngInstructions.currentIndex()
        newIndex = self.table_instructionsMngInstructions.model().index(index.row(), 0)
        newIndex2 = self.table_instructionsMngInstructions.model().index(index.row(), 1)

        self.selected_instruction_id = self.table_instructionsMngInstructions.model().data(
            newIndex)  # we can pass eid to the model
        # txt = self.table_instructionsMngInstructions.model().data(newIndex2)
        self.label_messagesMngInstructions.setText(f"row #{self.selected_instruction_id} is chosen")
        self.label_messagesMngInstructions.show()

        self.loadInstructionsToScreenFields()

    def initManageInstructionsComboBoxs(self):
        for item in VertexesEnum:  # VertexesEnum imported
            self.comboBox_vertex1MngInstructions.addItem(item.name + " " + str(item.value))
            self.comboBox_vertex2MngInstructions.addItem(item.name + " " + str(item.value))
            self.comboBox_vertex3MngInstructions.addItem(item.name + " " + str(item.value))

        for item in ['XY', 'XZ', 'YZ']:
            self.comboBox_axisMngInstructions.addItem(item)

    # alon
    def loadInstructionsDataForAlerts(self):
        headers = ['', 'Vertex1', 'Vertex2', 'Vertex3', 'Angle', 'Description', 'Axis']
        self.instructionAlertsData = DBConnection.getAllInstructions()
        self.instructionAlertsData = sorted(self.instructionAlertsData,
                                            key=lambda x: x[0])  # Sort data by instruction id
        self.instructionAlertsModel = TableModel(self.instructionAlertsData)
        self.instructionAlertsModel.setHeaderList(headers)
        self.instructionAlerts_proxy_model = QSortFilterProxyModel()
        self.instructionAlerts_proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.instructionAlerts_proxy_model.setSourceModel(self.instructionAlertsModel)
        self.instructionAlerts_proxy_model.sort(0, Qt.AscendingOrder)
        self.tb_instructionsMngAlerts.setModel(self.instructionAlerts_proxy_model)
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        # self.lineEdit_searchBarManageInstructions.textChanged.connect(self.instruction_proxy_model.setFilterFixedString)

    def instructionsAlertsTablePressed(self):
        index = self.tb_instructionsMngAlerts.currentIndex()
        newIndex = self.tb_instructionsMngAlerts.model().index(index.row(), 0)

        self.selected_instructionAlerts_id = self.tb_instructionsMngAlerts.model().data(
            newIndex)  # we can pass eid to the model
        self.lineEdit_instructionIdMngAlerts.setText(str(self.selected_instructionAlerts_id))
        # self.label_messagesMngInstructions.show()

        self.loadInstructionsAlerts(self.selected_instructionAlerts_id)
        self.tb_alertsMngAlerts.setColumnHidden(0, True)
        self.tb_alertsMngAlerts.setColumnHidden(1, True)
        self.tb_alertsMngAlerts.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tb_alertsMngAlerts.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

    def loadInstructionsAlerts(self, instruction_id):
        headers = ['', '', 'Text', 'Link']
        self.alertsData = DBConnection.getAlertsOfInstruction(instruction_id)
        self.alertsData = sorted(self.alertsData, key=lambda x: x[0])  # Sort data by instruction id
        self.alertsModel = TableModel(self.alertsData)
        self.alertsModel.setHeaderList(headers)
        self.alerts_proxy_model = QSortFilterProxyModel()
        self.alerts_proxy_model.setFilterKeyColumn(-1)  # Search all columns.
        self.alerts_proxy_model.setSourceModel(self.alertsModel)
        self.alerts_proxy_model.sort(0, Qt.AscendingOrder)
        self.tb_alertsMngAlerts.setModel(self.alerts_proxy_model)
        # You can choose the type of search by connecting to a different slot here.
        # see https://doc.qt.io/qt-5/qsortfilterproxymodel.html#public-slots
        # self.lineEdit_searchBarManageInstructions.textChanged.connect(self.instruction_proxy_model.setFilterFixedString)

    def alertsTablePressed(self):
        index = self.tb_alertsMngAlerts.currentIndex()
        newIndex = self.tb_alertsMngAlerts.model().index(index.row(), 2)
        newIndex2 = self.tb_alertsMngAlerts.model().index(index.row(), 3)
        newIndex3 = self.tb_alertsMngAlerts.model().index(index.row(), 0)

        self.selected_alerts_txt = self.tb_alertsMngAlerts.model().data(
            newIndex)
        self.selected_alerts_link = self.tb_alertsMngAlerts.model().data(
            newIndex2)
        self.selected_alert_id = self.tb_alertsMngAlerts.model().data(
            newIndex3)
        self.lineEdit_alertTxtMngAlerts.setText(str(self.selected_alerts_txt))
        self.lineEdit_LinkMngAlerts.setText(str(self.selected_alerts_link))

    def clearLabelsAndTextMngAlerts(self):
        self.lineEdit_instructionIdMngAlerts.setText('')
        self.lineEdit_alertTxtMngAlerts.setText('')
        self.lineEdit_LinkMngAlerts.setText('')
        self.tb_instructionsMngAlerts.clearSelection()
        self.tb_alertsMngAlerts.clearSelection()
        self.selected_instructionAlerts_id = -1
        self.label_messagesMngAlerts.hide()
        self.alerts_proxy_model.setSourceModel(None)
        self.loadInstructionsDataForAlerts()

    def checkEmptyFieldMngAlert(self):
        return self.lineEdit_instructionIdMngAlerts.text() == '' or self.lineEdit_alertTxtMngAlerts.text() == '' or self.lineEdit_LinkMngAlerts.text() == ''

    def addAlert(self):
        if self.checkEmptyFieldMngAlert():
            self.label_messagesMngAlerts.setText("Make sure all fields are filled")
            self.label_messagesMngAlerts.show()
            return
        if not self.lineEdit_instructionIdMngAlerts.text().isdigit():
            self.label_messagesMngAlerts.setText("Instruction id should be a number")
            self.label_messagesMngAlerts.show()
            return
        if DBConnection.checkIfInstructionExistAlerts(self.selected_instructionAlerts_id):
            self.label_messagesMngAlerts.setText("Wrong instruction id make sure this number exist!")
            self.label_messagesMngAlerts.show()
            return
        if DBConnection.checkIfAlertExist(self.selected_instructionAlerts_id, self.lineEdit_alertTxtMngAlerts.text(),
                                          self.lineEdit_LinkMngAlerts.text()):
            self.label_messagesMngAlerts.setText("Alert with same text and link for this instruction already exist!")
            self.label_messagesMngAlerts.show()
            return
        res = DBConnection.addNewAlert(self.selected_instructionAlerts_id,
                                       self.lineEdit_alertTxtMngAlerts.text(), self.lineEdit_LinkMngAlerts.text())
        if res:
            self.label_messagesMngAlerts.setText("Alert added")
            self.label_messagesMngAlerts.show()
            self.loadInstructionsAlerts(self.selected_instructionAlerts_id)

    def deleteAlert(self):
        if self.selected_alert_id == -1:
            self.label_messagesMngAlerts.setText("Please select alert from the second table")
            self.label_messagesMngAlerts.show()
            return
        res = DBConnection.delAlert(self.selected_alert_id)
        if res:
            self.label_messagesMngAlerts.setText("Alert deleted")
            self.label_messagesMngAlerts.show()
            self.loadInstructionsAlerts(self.selected_instructionAlerts_id)

    def updateAlert(self):
        if self.selected_alert_id == -1:
            self.label_messagesMngAlerts.setText("Please select alert from the second table")
            self.label_messagesMngAlerts.show()
            return
        if self.checkEmptyFieldMngAlert():
            self.label_messagesMngAlerts.setText("Make sure all fields are filled")
            self.label_messagesMngAlerts.show()
            return
        if not self.lineEdit_instructionIdMngAlerts.text().isdigit():
            self.label_messagesMngAlerts.setText("Instruction id should be a number")
            self.label_messagesMngAlerts.show()
            return
        if DBConnection.checkIfInstructionExistAlerts(self.selected_instructionAlerts_id):
            self.label_messagesMngAlerts.setText("Wrong instruction id make sure this number exist!")
            self.label_messagesMngAlerts.show()
            return
        if DBConnection.checkIfAlertExist(self.selected_instructionAlerts_id, self.lineEdit_alertTxtMngAlerts.text(),
                                          self.lineEdit_LinkMngAlerts.text()):
            self.label_messagesMngAlerts.setText("Alert with same text and link for this instruction already exist!")
            self.label_messagesMngAlerts.show()
            return
        res = DBConnection.modifyAlert(self.selected_alert_id, self.lineEdit_alertTxtMngAlerts.text(),
                                       self.lineEdit_LinkMngAlerts.text())
        if res:
            self.label_messagesMngAlerts.setText("Alert Updated")
            self.label_messagesMngAlerts.show()
            self.loadInstructionsAlerts(self.selected_instructionAlerts_id)


'''def openInstructionsWindow(self):
    if self.i_eid.text() != '':
        vid_id = DBConnection.getVideoId(self.i_eid.text())
        ins = WatchExerciseInstructions(vid_id, self.i_eid.text())
        ins.show()
        self.lbl_alert.hide()
    else:
        self.lbl_alert.show()'''

'''def closeEvent(self, event):
    print("The user: " + self.current_user.first_name + ' ' + self.current_user.last_name + ' ' + "logged out!")
    DBConnection.logOutCurrentUser(self.current_user.user_id)'''

# ToDo:
'''
   Check that delete exercise is working - delete all instructions as well?
'''
