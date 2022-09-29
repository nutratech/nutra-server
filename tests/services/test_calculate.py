"""Test cases for the calculate service"""
from typing import Dict, List, Tuple

import pytest

import ntserv.services.calculate as calc
from ntserv.services import Gender


# ------------------------------------------------
# 1 rep max
# ------------------------------------------------
def _check_orm_results(
    maxes: Dict[int, float], expected_results: List[Tuple[int, float]]
) -> None:
    """Asserts expected foreach result"""
    for n_reps, expected_max in expected_results:
        assert maxes[n_reps] == expected_max


@pytest.mark.parametrize(
    "reps,weight,expected_results",
    [
        (3, 315, [(1, 336.0)]),
        (8, 275, [(1, 339.2)]),
        (10, 225, [(1, 292.5)]),
        (12, 225, [(1, 307.5)]),
        (15, 225, [(1, 330.0)]),
        (20, 225, [(1, 367.5)]),
    ],
)
def test_orm_epley(reps, weight, expected_results):
    """Tests the Epley 1 rep max equation"""
    maxes = calc.orm_epley(reps, weight)
    _check_orm_results(maxes, expected_results)


@pytest.mark.parametrize(
    "reps,weight,expected_results",
    [
        (3, 315, [(1, 333.5)]),
        (8, 275, [(1, 341.4)]),
        (10, 225, [(1, 300.0)]),
        (12, 225, [(1, 324.0)]),
        # NOTE: Brzycki loses accuracy > 12 reps (tends to overestimate)
        (15, 225, [(1, 368.2)]),
        (20, 225, [(1, 476.5)]),
    ],
)
def test_orm_brzycki(reps, weight, expected_results):
    """Tests the Brzycki 1 rep max equation"""
    maxes = calc.orm_brzycki(reps, weight)
    _check_orm_results(maxes, expected_results)


@pytest.mark.parametrize(
    "reps,weight,expected_results",
    [
        # NOTE: dos Remedios only supports select rep counts
        (3, 315, [(1, 350.0)]),
        (8, 275, [(1, 366.7)]),
        (10, 225, [(1, 321.4)]),
        (12, 225, [(1, 346.2)]),
        (15, 225, [(1, 375.0)]),
    ],
)
def test_orm_dos_remedios(reps, weight, expected_results):
    """Tests the dosRemedios 1 rep max equation"""
    maxes = calc.orm_dos_remedios(reps, weight)
    _check_orm_results(maxes, expected_results)


# ------------------------------------------------
# BMR
# ------------------------------------------------
def test_bmr_katch_mcardle():
    """Tests the Katch-McArdle BMR equation"""


def test_bmr_cunningham():
    """Tests the Cunningham BMR equation"""


@pytest.mark.parametrize(
    "gender,weight,height,dob,activity_factor,expected_result",
    [
        (Gender.MALE, 77, 177, 725864400, 0.55, {"bmr": 1739, "tdee": 2695}),
        (Gender.FEMALE, 77, 177, 725864400, 0.55, {"bmr": 1573, "tdee": 2438}),
    ],
)
def test_bmr_mifflin_st_jeor(
    gender, weight, height, dob, activity_factor, expected_result
):
    """Tests the Mifflin-St. Jeor BMR equation"""
    result = calc.bmr_mifflin_st_jeor(gender, weight, height, dob, activity_factor)
    assert result == expected_result


@pytest.mark.parametrize(
    "gender,weight,height,dob,activity_factor,expected_result",
    [
        (Gender.MALE, 77, 177, 725864400, 0.55, {"bmr": 1800, "tdee": 2791}),
        (Gender.FEMALE, 77, 177, 725864400, 0.55, {"bmr": 1579, "tdee": 2448}),
    ],
)
def test_bmr_harris_benedict(
    gender, weight, height, dob, activity_factor, expected_result
):
    """Tests the Harris-Benedict BMR equation"""
    result = calc.bmr_harris_benedict(gender, weight, height, dob, activity_factor)
    assert result == expected_result
