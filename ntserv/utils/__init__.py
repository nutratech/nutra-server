"""General utilities & helper methods"""
from enum import Enum


class Gender(Enum):
    """
    A validator and Enum class for gender inputs; used in several calculations.
    NOTE: floating point -1 to 1, or 0 to 1... for non-binary?
    """

    MALE = "MALE"
    FEMALE = "FEMALE"
