class ExerciseInstruction:
    def __init__(self, exerciseInstructionId, exerciseId, instructionId, alertId,
                 deviationPositive, deviationNegative, instructionStage, exerciseInstructionType,
                 alertDeviationTrigger, alertExtendedId) -> None:
        self.exerciseInstructionId = exerciseInstructionId
        self.exerciseId = exerciseId
        self.instructionId = instructionId
        self.alertId = alertId
        self.deviationPositive = deviationPositive
        self.deviationNegative = deviationNegative
        self.instructionStage = instructionStage
        self.exerciseInstructionType = exerciseInstructionType
        self.alertDeviationTrigger = alertDeviationTrigger
        self.alertExtendedId = alertExtendedId