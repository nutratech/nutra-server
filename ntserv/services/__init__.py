"""Supporting methods for calculate service"""
from enum import Enum


class ActivityFactor(Enum):
    """
    Used in BMR calculations.
    Different activity levels: {0.200, 0.375, 0.550, 0.725, 0.900}
    @todo Verify the accuracy of these "names". Access by index?
    """

    SEDENTARY = 0.2
    MILDLY_ACTIVE = 0.375
    ACTIVE = 0.55
    HIGHLY_ACTIVE = 0.725
    INTENSELY_ACTIVE = 0.9


def activity_factor_from_float(activity_factor: float) -> ActivityFactor:
    """Gets ActivityFactor Enum by float value if it exists, else raise ValueError"""
    for enum_entry in ActivityFactor:
        if activity_factor == enum_entry.value:
            return enum_entry
    raise ValueError(f"No such ActivityFactor for value: {activity_factor}")


class Gender(Enum):
    """
    A validator and Enum class for gender inputs; used in several calculations.
    NOTE: floating point -1 to 1, or 0 to 1... for non-binary?
    """

    MALE = "MALE"
    FEMALE = "FEMALE"
