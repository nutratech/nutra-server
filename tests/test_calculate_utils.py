import pytest

import ntserv.utils.calculate as calc


# ------------------------------------------------
# 1 rep max
# ------------------------------------------------
def _check_orm_results(maxes, expected_results):
    for n_reps, expected_max in expected_results:
        assert maxes[n_reps] == expected_max


@pytest.mark.parametrize(
    "reps,weight,expected_results",
    [
        (3, 315, [(1, 346.5)]),
        (8, 275, [(1, 348.3)]),
        (10, 225, [(1, 300.0)]),
        (12, 225, [(1, 315.0)]),
        (15, 225, [(1, 337.5)]),
        (20, 225, [(1, 375.0)]),
    ],
)
def test_orm_epley(reps, weight, expected_results):
    maxes = calc.orm_epley(reps, weight)
    _check_orm_results(maxes, expected_results)


@pytest.mark.parametrize(
    "reps,weight,expected_results",
    [
        (3, 315, [(1, 333.5)]),
        (8, 275, [(1, 341.4)]),
        (10, 225, [(1, 300.0)]),
        (12, 225, [(1, 324.0)]),
        # NOTE: Brzycki loses accuracy > 12 reps
        (15, 225, [(1, 368.2)]),
        (20, 225, [(1, 476.5)]),
    ],
)
def test_orm_brzycki(reps, weight, expected_results):
    maxes = calc.orm_brzycki(reps, weight)
    _check_orm_results(maxes, expected_results)


# ------------------------------------------------
# BMR
# ------------------------------------------------
