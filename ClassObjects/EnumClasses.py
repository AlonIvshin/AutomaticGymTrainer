from enum import Enum


class E_ExerciseInstructionType(Enum):
    STATIC = 0
    DYNAMIC = 1


class E_AlertDeviationTrigger(Enum):
    POSITIVE = 1
    BOTH = 0
    NEGATIVE = -1


class E_InstructionAxis(Enum):
    XY = 1
    XZ = 2
    YZ = 3
