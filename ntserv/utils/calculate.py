#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 20:53:14 2020

@author: shane
"""

from datetime import datetime

# TODO: generalize activity level across BMR calcs, e.g. LIGHT, MODERATE, EXTREME


# ------------------------------------------------
# 1 rep max
# ------------------------------------------------
def orm_epley(reps: float, weight: float) -> dict:
    """
    Source: https://workoutable.com/one-rep-max-calculator/

    1 RM = weight * (1 + reps / 30)

    Returns a dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 8, 10, 12, 15, 20)
    """

    maxes = {1: round(weight * (1 + reps / 30), 1)}
    return maxes


def orm_brzycki(reps: float, weight: float) -> dict:
    """
    Source: https://workoutable.com/one-rep-max-calculator/

    1 RM = weight * 36 / (37 - reps)

    Returns a dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 8, 10, 12, 15, 20)
    """

    maxes = {1: round(weight * 36 / (37 - reps), 1)}
    return maxes


# ------------------------------------------------
# BMR
# ------------------------------------------------
def bmr_katch_mcardle(lbm, activity_factor):
    """
    BMR = 370 + (21.6 x Lean Body Mass(kg) )

    Source: https://www.calculatorpro.com/calculator/katch-mcardle-bmr-calculator/
    Source: https://tdeecalculator.net/about.php
    """
    bmr = 370 + (21.6 * lbm)
    tdee = bmr * (1 + activity_factor)
    return round(bmr), round(tdee)


def bmr_cunningham(lbm, activity_factor):
    """
    Source:
        <https://www.slideshare.net/lsandon/weight-management-in-athletes-lecture>
    """
    bmr = 500 + 22 * lbm
    tdee = bmr * (1 + activity_factor)
    return round(bmr), round(tdee)


def bmr_mifflin_st_jeor(gender, weight, height, dob, activity_factor):
    """
    Activity Factor
    ---------------
    0.200 = sedentary (little or no exercise)

    0.375 = lightly active
        (light exercise/sports 1-3 days/week, approx. 590 Cal/day)

    0.550 = moderately active
        (moderate exercise/sports 3-5 days/week, approx. 870 Cal/day)

    0.725 = very active
        (hard exercise/sports 6-7 days a week, approx. 1150 Cal/day)

    0.900 = extra active
        (very hard exercise/sports and physical job, approx. 1580 Cal/day)

    Source: <https://www.myfeetinmotion.com/mifflin-st-jeor-equation/>
    """
    _bmr = 10 * weight + 6.25 + 6.25 * height - 5 * _age(dob)
    if gender == "MALE":
        bmr = _bmr + 5
    elif gender == "FEMALE":
        bmr = _bmr - 161

    tdee = bmr * (1 + activity_factor)
    return round(bmr), round(tdee)


def bmr_harris_benedict(gender, weight, height, dob, activity_factor):
    """
    Harris-Benedict = (13.397m + 4.799h - 5.677a) + 88.362 (MEN)
    Harris-Benedict = (9.247m + 3.098h - 4.330a) + 447.593 (WOMEN)

    m is mass in kg, h is height in cm, a is age in years

    Source: <https://tdeecalculator.net/about.php>
    """
    age = _age(dob)

    if gender == "MALE":
        bmr = (13.397 * weight + 4.799 * height - 5.677 * age) + 88.362
    elif gender == "FEMALE":
        bmr = (9.247 * weight + 3.098 * height - 4.330 * age) + 447.593

    tdee = bmr * (1 + activity_factor)
    return round(bmr), round(tdee)


# ------------------------------------------------
# Misc functions
# ------------------------------------------------
def _age(dob: int):
    now = datetime.now().timestamp()
    years = (now - dob) / (365 * 24 * 3600)
    return years
