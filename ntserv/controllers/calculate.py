# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 16:47:18 2020

@author: shane
"""

import math
import traceback
from typing import Dict, Union

import sanic.response
from sanic import html
from tabulate import tabulate

import ntserv.services.calculate as calc
import ntserv.utils.libserver as server
from ntserv.services import Gender, activity_factor_from_float
from ntserv.utils import cache


def get_nutrients(**kwargs: dict) -> sanic.HTTPResponse:
    """Archaic method (not used currently). Returns nutrients as JSON or HTML"""
    response_type = kwargs.get("response_type")
    nutrients = list(cache.NUTRIENTS.values())

    if response_type == "HTML":
        table = tabulate(nutrients, headers="keys", tablefmt="presto")
        return html(f"<pre>{table}</pre>")
    # else: JSON
    return server.Response200Success(data=nutrients)


def post_calc_1rm(request: sanic.Request) -> sanic.HTTPResponse:
    """Calculates a few different 1 rep max possibilities"""
    body = request.json

    reps = int(body["reps"])
    weight = float(body["weight"])

    # Compute 3 one-rep max equations
    # NOTE: each service-level call handles errors internally
    epley = calc.orm_epley(reps, weight)
    brzycki = calc.orm_brzycki(reps, weight)
    dos_remedios = calc.orm_dos_remedios(reps, weight)

    return server.Response200Success(
        data={
            "epley": epley,
            "brzycki": brzycki,
            "dosRemedios": dos_remedios,
        }
    )


def post_calc_bmr(request: sanic.Request) -> sanic.HTTPResponse:
    """
    Calculates all types of BMR for comparison

    @param request: body: weight (kg), height (cm), gender, dob (int), activity_factor,
        lbm | bodyFat
    @return: dict with "katchMcArdle", "cunningham", "mifflinStJeor",
        and "harrisBenedict"
    """
    body = request.json

    # NOTE: doesn't support imperial units

    # TODO: enum class for this? And gender?
    activity_factor = activity_factor_from_float(float(body["activityFactor"]))
    weight = float(body["weight"])  # kg
    height = float(body["height"])  # cm
    gender = Gender(body["gender"])  # ['MALE', 'FEMALE']
    dob = int(body["dob"])  # unix (epoch) timestamp

    # TODO: validate this against a REQUIRES: {lbm || bf}
    if "lbm" in body:
        lbm = float(body["lbm"])
    else:
        body_fat = float(body["bodyFat"])
        lbm = weight * (1 - body_fat)

    # Compute 3 different BMR equations
    katch_mcardle = calc.bmr_katch_mcardle(lbm, activity_factor)
    cunningham = calc.bmr_cunningham(lbm, activity_factor)
    mifflin_st_jeor = calc.bmr_mifflin_st_jeor(
        gender, weight, height, dob, activity_factor
    )
    harris_benedict = calc.bmr_harris_benedict(
        gender, weight, height, dob, activity_factor
    )

    return server.Response200Success(
        data={
            "katchMcArdle": katch_mcardle,
            "cunningham": cunningham,
            "mifflinStJeor": mifflin_st_jeor,
            "harrisBenedict": harris_benedict,
        }
    )


def post_calc_body_fat(request: sanic.Request) -> sanic.HTTPResponse:
    """
    Doesn't support imperial units yet.

    @return: dict, with "navy", "threeSite", and "sevenSite",
        with potential validation errors inside those objects.
    """
    body = request.json

    # TODO: register this as 400 error, populate similar err_msg property (as 500 does)
    gender = Gender(body["gender"])

    # Initialize result variables
    navy: Union[float, Dict[str, str]]
    three_site: Union[float, Dict[str, str]]
    seven_site: Union[float, Dict[str, str]]

    # Calculate 3 different body fat equations
    try:
        navy = calc.bf_navy(gender, body)
    except (KeyError, ValueError) as err:
        # TODO: helper method to bundle up exception errors on nested objects, like this
        navy = {
            "errMsg": f"Bad request — {repr(err)}",
            "stack": traceback.format_exc(),
        }
    try:
        three_site = calc.bf_3site(gender, body)
    except (KeyError, ValueError) as err:
        # TODO: helper method to bundle up exception errors on nested objects, like this
        three_site = {
            "errMsg": f"Bad request — {repr(err)}",
            "stack": traceback.format_exc(),
        }
    try:
        seven_site = calc.bf_7site(gender, body)
    except (KeyError, ValueError) as err:
        # TODO: helper method to bundle up exception errors on nested objects, like this
        seven_site = {
            "errMsg": f"Bad request — {repr(err)}",
            "stack": traceback.format_exc(),
        }

    return server.Response200Success(
        data={"navy": navy, "threeSite": three_site, "sevenSite": seven_site}
    )


def post_calc_lb_limits(request: sanic.Request) -> sanic.HTTPResponse:
    """Calculate mens' lean body limits"""
    body = dict(request.json)
    height = float(body["height"])

    desired_bf = float(body.get("desired-bf", -1))

    wrist = float(body.get("wrist", -1))
    ankle = float(body.get("ankle", -1))

    # NOTE: doesn't support SI / metrics units
    # TODO: move to calculate.py in utils, not controllers. Add docstrings and source(s)

    # ----------------
    # Martin Berkhan
    # ----------------
    _min = round((height - 102) * 2.205, 1)
    _max = round((height - 98) * 2.205, 1)
    martin_berkhan = {"notes": "Contest shape (5-6%)", "weight": f"{_min} ~ {_max} lbs"}

    # ----------------
    # Eric Helms
    # ----------------
    try:
        _min = round(4851.00 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
        _max = round(5402.25 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
        eric_helms = {
            "notes": f"{desired_bf}% bodyfat",
            "weight": f"{_min} ~ {_max} lbs",
        }
    except TypeError:
        eric_helms = {"errMsg": 'MISSING_INPUT — requires: ["height", "desired-bf"]'}

    # ----------------
    # Casey Butt, PhD
    # ----------------
    try:
        height = height / 2.54
        weight = wrist / 2.54
        ankle = ankle / 2.54
        lbm = round(
            height ** (3 / 2)
            * (math.sqrt(weight) / 22.6670 + math.sqrt(ankle) / 17.0104)
            * (1 + desired_bf / 224),
            1,
        )
        weight = round(lbm / (1 - desired_bf / 100), 1)
        casey_butt = {
            "notes": f"{desired_bf}% bodyfat",
            "lbm": f"{lbm} lbs",
            "weight": f"{weight} lbs",
            "chest": round(1.6817 * weight + 1.3759 * ankle + 0.3314 * height, 2),
            "arm": round(1.2033 * weight + 0.1236 * height, 2),
            "forearm": round(0.9626 * weight + 0.0989 * height, 2),
            "neck": round(1.1424 * weight + 0.1236 * height, 2),
            "thigh": round(1.3868 * ankle + 0.1805 * height, 2),
            "calf": round(0.9298 * ankle + 0.1210 * height, 2),
        }
    except TypeError:
        casey_butt = {
            "errMsg": "MISSING_INPUT — "
            + 'requires: ["height", "desired-bf", "wrist", "ankle"]',
        }

    return server.Response200Success(
        data={
            "martinBerkhan": martin_berkhan,
            "ericHelms": eric_helms,
            "caseyButt": casey_butt,
        }
    )
