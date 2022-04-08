import sys
import welcomscreen
import chooseexercise
from PyQt5.QtWidgets import QApplication

import workoutestimation

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #welcome = welcomscreen.WelcomeScreen()
    # choose = chooseexercise.ChooseExerciseScreen()
    # choose.show()
    #welcome.show()
    wo_est = workoutestimation.EstimationScreen(1, 4)
    wo_est.show()


    try:
        sys.exit(app.exec_())

    except:
        print("Exiting")
