#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 20:53:14 2020

@author: shane
"""
import traceback
from datetime import datetime

from ntserv.utils.logger import get_logger

# TODO: generalize activity level across BMR calcs, e.g. LIGHT, MODERATE, EXTREME

_logger = get_logger(__name__)

# ------------------------------------------------
# 1 rep max
# ------------------------------------------------

common_n_reps = (1, 2, 3, 5, 6, 8, 10, 12, 15, 20)


def orm_epley(reps: float, weight: float) -> dict:
    """
    Returns a dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 6, 8, 10, 12, 15, 20)

    1 RM = weight * (1 + (reps - 1) / 30)

    Source: https://workoutable.com/one-rep-max-calculator/
    """

    def one_rm() -> float:
        _un_rounded_result = weight * (1 + (reps - 1) / 30)
        return round(_un_rounded_result, 1)

    def weight_max_reps(target_reps: float) -> float:
        _un_rounded_result = one_rm() / (1 + (target_reps - 1) / 30)
        return round(_un_rounded_result, 1)

    maxes = {n_reps: weight_max_reps(n_reps) for n_reps in common_n_reps}
    return maxes


def orm_brzycki(reps: float, weight: float) -> dict:
    """
    Returns a dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 6, 8, 10, 12, 15)

    1 RM = weight * 36 / (37 - reps)

    Source: https://workoutable.com/one-rep-max-calculator/
    """

    def _one_rm() -> float:
        _un_rounded_result = weight * 36 / (37 - reps)
        return round(_un_rounded_result, 1)

    one_rm = _one_rm()

    def weight_max_reps(target_reps: float) -> float:
        _un_rounded_result = one_rm / (1 + (target_reps - 1) / 30)
        return round(_un_rounded_result, 1)

    maxes = {n_reps: weight_max_reps(n_reps) for n_reps in common_n_reps}
    return maxes


def orm_dos_remedios(reps: int, weight: float) -> dict:
    """
    Returns a dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 6, 8, 10, 12, 15)

    Source:
        https://www.peterrobertscoaching.com/blog/the-best-way-to-calculate-1-rep-max
    """

    _common_n_reps = {
        1: 1,
        2: 0.92,
        3: 0.9,
        5: 0.87,
        6: 0.82,
        8: 0.75,
        10: 0.7,
        12: 0.65,
        15: 0.6,
    }

    def _one_rm() -> float:
        _multiplier = _common_n_reps[reps]
        _un_rounded_result = weight / _multiplier
        return round(_un_rounded_result, 1)

    try:
        one_rm = _one_rm()
    except KeyError:
        _logger.debug(traceback.format_exc())
        valid_reps = list(_common_n_reps.keys())
        return {
            "error": "INVALID_RANGE",
            "requires": ["reps", "in", valid_reps, "got", reps],
        }

    def max_weight(target_reps: int) -> float:
        _multiplier = _common_n_reps[target_reps]
        _un_rounded_result = one_rm * _multiplier
        return round(_un_rounded_result, 1)

    return {n_reps: max_weight(n_reps) for n_reps in _common_n_reps}


# ------------------------------------------------
# BMR
# ------------------------------------------------
def bmr_katch_mcardle(lbm: float, activity_factor: float):
    """
    @param lbm: lean mass in kg
    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}

    BMR = 370 + (21.6 x Lean Body Mass(kg) )

    Source: https://www.calculatorpro.com/calculator/katch-mcardle-bmr-calculator/
    Source: https://tdeecalculator.net/about.php
    """

    bmr = 370 + (21.6 * lbm)
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


def bmr_cunningham(lbm: float, activity_factor: float):
    """
    @param lbm: lean mass in kg
    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}

    Source: https://www.slideshare.net/lsandon/weight-management-in-athletes-lecture
    """

    bmr = 500 + 22 * lbm
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


def bmr_mifflin_st_jeor(
    gender: str, weight: float, height: float, dob: int, activity_factor: float
) -> dict:
    """
    @param gender: {'MALE', 'FEMALE'}
    @param weight: kg
    @param height: cm
    @param dob: int, unix timestamp (seconds)
    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}

    Activity Factor\n
    ---------------\n
    0.200 = sedentary (little or no exercise)

    0.375 = lightly active
        (light exercise/sports 1-3 days/week, approx. 590 Cal/day)

    0.550 = moderately active
        (moderate exercise/sports 3-5 days/week, approx. 870 Cal/day)

    0.725 = very active
        (hard exercise/sports 6-7 days a week, approx. 1150 Cal/day)

    0.900 = extra active
        (very hard exercise/sports and physical job, approx. 1580 Cal/day)

    Source: https://www.myfeetinmotion.com/mifflin-st-jeor-equation/
    """

    def gender_specific(_gender: str, _bmr: float) -> float:
        func = {
            "MALE": lambda x: x + 5,
            "FEMALE": lambda x: x - 161,
        }
        # TODO: would we rather enforce gender, or avoid mypy "errors" with lambdas
        return func[_gender](_bmr)  # type: ignore

    bmr = 10 * weight + 6.25 + 6.25 * height - 5 * _age(dob)

    bmr = gender_specific(gender, bmr)
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


def bmr_harris_benedict(
    gender: str, weight: float, height: float, dob: int, activity_factor: float
):
    """
    @param gender: {'MALE', 'FEMALE'}
    @param weight: kg
    @param height: cm
    @param dob: int, unix timestamp (seconds)
    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}

    Harris-Benedict = (13.397m + 4.799h - 5.677a) + 88.362 (MEN)

    Harris-Benedict = (9.247m + 3.098h - 4.330a) + 447.593 (WOMEN)

    m is mass in kg, h is height in cm, a is age in years

    Source: https://tdeecalculator.net/about.php
    """

    def gender_specific(_gender: str) -> float:
        age = _age(dob)

        func = {
            "MALE": lambda: (13.397 * weight + 4.799 * height - 5.677 * age) + 88.362,
            "FEMALE": lambda: (9.247 * weight + 3.098 * height - 4.330 * age) + 447.593,
        }

        return func[_gender]()  # type: ignore

    bmr = gender_specific(gender)
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


# ------------------------------------------------
# Misc functions
# ------------------------------------------------
def _age(dob: int):
    now = datetime.now().timestamp()
    years = (now - dob) / (365 * 24 * 3600)
    return years
