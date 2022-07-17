#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 16:47:18 2020

@author: shane
"""

import math
import traceback

import sanic.response
from sanic import html
from tabulate import tabulate

import ntserv.services.calculate as calc
from ntserv.utils import Gender, cache
from ntserv.utils.libserver import Success200Response

# pylint: disable=invalid-name

# TODO: import the above and reference from e.g. libserver.Success200Response


def get_nutrients(**kwargs) -> sanic.HTTPResponse:
    response_type = kwargs.get("response_type")
    nutrients = list(cache.NUTRIENTS.values())

    if response_type == "HTML":
        table = tabulate(nutrients, headers="keys", tablefmt="presto")
        return html(f"<pre>{table}</pre>")
    # else: JSON
    return Success200Response(data=nutrients)


def post_calc_1rm(request):
    """Calculates a few different 1 rep max possibilities"""
    body = request.json

    reps = int(body["reps"])
    weight = float(body["weight"])

    # Compute 3 one-rep max equations
    # NOTE: each service-level call handles errors internally
    epley = calc.orm_epley(reps, weight)
    brzycki = calc.orm_brzycki(reps, weight)
    dos_remedios = calc.orm_dos_remedios(reps, weight)

    return Success200Response(
        data={
            "epley": epley,
            "brzycki": brzycki,
            "dos_remedios": dos_remedios,
        }
    )


def post_calc_bmr(request):
    """Calculates all types of BMR for comparison"""
    body = request.json

    # NOTE: doesn't support imperial units

    # TODO: enum class for this? And gender?
    activity_factor = float(body["activity_factor"])
    weight = float(body["weight"])  # kg
    height = float(body["height"])  # cm
    gender = body["gender"]  # ['MALE', 'FEMALE']
    dob = int(body["dob"])  # unix (epoch) timestamp

    lbm = body.get("lbm")
    # TODO: validate this against a REQUIRES: {lbm || bf}
    if lbm:
        lbm = float(lbm)
    else:
        bf = float(body["bodyfat"])
        lbm = weight * (1 - bf)

    # Compute 3 different BMR equations
    katch_mcardle = calc.bmr_katch_mcardle(lbm, activity_factor)
    cunningham = calc.bmr_cunningham(lbm, activity_factor)
    mifflin_st_jeor = calc.bmr_mifflin_st_jeor(
        gender, weight, height, dob, activity_factor
    )
    harris_benedict = calc.bmr_harris_benedict(
        gender, weight, height, dob, activity_factor
    )

    return Success200Response(
        data={
            "Katch-McArdle": katch_mcardle,
            "Cunningham": cunningham,
            "Mifflin-St-Jeor": mifflin_st_jeor,
            "Harris-Benedict": harris_benedict,
        }
    )


def post_calc_body_fat(request):
    """
    Doesn't support imperial units yet.

    @param request: HTTPRequest
    @return: dict, with "navy", "threeSite", and "sevenSite",
        with potential validation errors inside those objects.
    """
    body = request.json

    # TODO: register this as 400 error, populate similar err_msg property as 500 does
    gender = Gender(body["gender"])

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

    return Success200Response(
        data={"navy": navy, "threeSite": three_site, "sevenSite": seven_site}
    )


def post_calc_lb_limits(request):
    body = request.json
    height = float(body["height"])

    desired_bf = body.get("desired-bf")

    wrist = body.get("wrist")
    ankle = body.get("ankle")

    # NOTE: doesn't support SI / metrics units
    # TODO: move to calculate.py in utils, not controllers. Add docstrings and source(s)

    # ----------------
    # Martin Berkhan
    # ----------------
    _min = round((height - 102) * 2.205, 1)
    _max = round((height - 98) * 2.205, 1)
    mb = {"notes": "Contest shape (5-6%)", "weight": f"{_min} ~ {_max} lbs"}

    # ----------------
    # Eric Helms
    # ----------------
    try:
        _min = round(4851.00 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
        _max = round(5402.25 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
        eh = {"notes": f"{desired_bf}% bodyfat", "weight": f"{_min} ~ {_max} lbs"}
    except TypeError:
        eh = {"errMsg": 'MISSING_INPUT — requires: ["height", "desired-bf"]'}

    # ----------------
    # Casey Butt, PhD
    # ----------------
    try:
        h = height / 2.54
        w = wrist / 2.54
        a = ankle / 2.54
        lbm = round(
            h ** (3 / 2)
            * (math.sqrt(w) / 22.6670 + math.sqrt(a) / 17.0104)
            * (1 + desired_bf / 224),
            1,
        )
        weight = round(lbm / (1 - desired_bf / 100), 1)
        cb = {
            "notes": f"{desired_bf}% bodyfat",
            "lbm": f"{lbm} lbs",
            "weight": f"{weight} lbs",
            "chest": round(1.6817 * w + 1.3759 * a + 0.3314 * h, 2),
            "arm": round(1.2033 * w + 0.1236 * h, 2),
            "forearm": round(0.9626 * w + 0.0989 * h, 2),
            "neck": round(1.1424 * w + 0.1236 * h, 2),
            "thigh": round(1.3868 * a + 0.1805 * h, 2),
            "calf": round(0.9298 * a + 0.1210 * h, 2),
        }
    except TypeError:
        cb = {
            "errMsg": "MISSING_INPUT — "
            + 'requires: ["height", "desired-bf", "wrist", "ankle"]',
        }

    return Success200Response(
        data={"martin-berkhan": mb, "eric-helms": eh, "casey-butt": cb}
    )
