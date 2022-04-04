class Instruction:
    def __init__(self, instructionId, vertex1, vertex2, vertex3, angle, description, instructionAxis) -> None:
        self.instructionId = instructionId
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.vertex3 = vertex3
        self.angle = angle
        self.description = description
        self.instructionAxis = instructionAxis
        self.instructionAlertData = None  # Alert Object
