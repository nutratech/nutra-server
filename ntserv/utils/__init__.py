from enum import Enum


class Gender(Enum):
    # NOTE: floating point -1 to 1, or 0 to 1... for non-binary?
    MALE = "MALE"
    FEMALE = "FEMALE"
