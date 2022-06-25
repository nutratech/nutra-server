#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 16:47:18 2020

@author: shane
"""

import math

import sanic.response
from sanic import html
from tabulate import tabulate

from ntserv.utils import cache
from ntserv.utils.calculate import (
    bmr_cunningham,
    bmr_harris_benedict,
    bmr_katch_mcardle,
    bmr_mifflin_st_jeor,
)
from ntserv.utils.libserver import NotImplemented501Response, Success200Response

# TODO: import the above and reference from e.g. libserver.Success200Response

# TODO: solve this by supporting *args, **kwargs
# pylint: disable=unused-argument


def get_nutrients(request, response_type="JSON") -> sanic.HTTPResponse:
    nutrients = list(cache.NUTRIENTS.values())

    if response_type == "JSON":
        # TODO: fix dict to accept either dict or list
        return Success200Response(data=nutrients)
    # else: HTML
    table = tabulate(nutrients, headers="keys", tablefmt="presto")
    return html(f"<pre>{table}</pre>")


def post_calc_1rm(request):
    """Calculates a few different 1 rep max possibilities"""
    body = request.json

    reps = body["reps"]
    weight = body["weight"]

    print(reps)
    print(weight)
    return NotImplemented501Response()

    # TODO: tell them how many they can hit for 2, 3, 5, 8, 10, 12, 15, and 20


def post_calc_bmr(request):
    """Calculates all types of BMR for comparison"""
    body = request.json

    # NOTE: doesn't support imperial units

    activity_factor = float(body["activity_factor"])  # TODO: int, float, or string?
    weight = float(body["weight"])  # kg
    height = float(body["height"])  # cm
    gender = body["gender"]  # ['MALE', 'FEMALE']
    dob = int(body["dob"])  # unix (epoch) timestamp

    lbm = body.get("lbm")
    if lbm:
        lbm = float(lbm)
    else:
        bf = float(body["bodyfat"])
        lbm = weight * (1 - bf)

    # TODO: each of these methods returns a tuple: (bmr, tdee). Do we want a dict?
    katch_mcardle = bmr_katch_mcardle(lbm, activity_factor)
    cunningham = bmr_cunningham(lbm, activity_factor)
    mifflin_st_jeor = bmr_mifflin_st_jeor(gender, weight, height, dob, activity_factor)
    harris_benedict = bmr_harris_benedict(gender, weight, height, dob, activity_factor)

    return Success200Response(
        data={
            "Katch-McArdle": katch_mcardle,
            "Cunningham": cunningham,
            "Mifflin-St-Jeor": mifflin_st_jeor,
            "Harris-Benedict": harris_benedict,
        }
    )


def post_calc_body_fat(request):
    body = request.json

    gender = body["gender"]
    age = body["age"]
    height = body["height"]

    # Navy measurements
    waist = body.get("waist")
    if gender == "FEMALE":
        hip = body.get("hip")
    neck = body.get("neck")

    # 3-site calipers
    chest = body.get("chest")
    ab = body.get("ab")
    thigh = body.get("thigh")

    # 7-site calipers
    tricep = body.get("tricep")
    sub = body.get("sub")
    sup = body.get("sup")
    mid = body.get("mid")

    # NOTE: doesn't support imperial units
    # TODO: move to calculate.py in utils, not controllers. Add docstrings and source(s)

    # ----------------
    # Navy test
    # ----------------
    if gender == "MALE":
        denom = (
            1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)
        )
    elif gender == "FEMALE":
        denom = (
            1.29579
            - 0.35004 * math.log10(waist + hip - neck)
            + 0.22100 * math.log10(height)
        )
    else:
        denom = 1
    navy = round(495 / denom - 450, 2)

    # ----------------
    # 3-site test
    # ----------------
    s3 = chest + ab + thigh
    if gender == "MALE":
        denom = 1.10938 - 0.0008267 * s3 + 0.0000016 * s3 * s3 - 0.0002574 * age
    elif gender == "FEMALE":
        denom = 1.089733 - 0.0009245 * s3 + 0.0000025 * s3 * s3 - 0.0000979 * age
    else:
        denom = 1
    three_site = round(495 / denom - 450, 2)

    # ----------------
    # 7-site test
    # ----------------
    s7 = chest + ab + thigh + tricep + sub + sup + mid
    if gender == "MALE":
        denom = 1.112 - 0.00043499 * s7 + 0.00000055 * s7 * s7 - 0.00028826 * age
    elif gender == "FEMALE":
        denom = 1.097 - 0.00046971 * s7 + 0.00000056 * s7 * s7 - 0.00012828 * age
    else:
        denom = 1
    seven_site = round(495 / denom - 450, 2)

    return Success200Response(
        data={"navy": navy, "three-site": three_site, "seven-site": seven_site}
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
    min = round((height - 102) * 2.205, 1)
    max = round((height - 98) * 2.205, 1)
    mb = {"notes": "Contest shape (5-6%)", "weight": f"{min} ~ {max} lbs"}

    # ----------------
    # Eric Helms
    # ----------------
    try:
        min = round(4851.00 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
        max = round(5402.25 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
        eh = {"notes": f"{desired_bf}% bodyfat", "weight": f"{min} ~ {max} lbs"}
    except TypeError:
        eh = {"error": "MISSING_INPUT", "requires": ["height", "desired-bf"]}

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
            "error": "MISSING_INPUT",
            "requires": ["height", "desired-bf", "wrist", "ankle"],
        }

    return Success200Response(
        data={"martin-berkhan": mb, "eric-helms": eh, "casey-butt": cb}
    )
