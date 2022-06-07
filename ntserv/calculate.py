#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 16:47:18 2020

@author: shane

This file is part of nutra-server, a server for nutra clients.
    https://github.com/gamesguru/nutra-server

nutra-server is a server for nutra clients.
Copyright (C) 2019-2020  Shane Jaroch

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import math

from tabulate import tabulate

from ntserv.libserver import Success200Response
from ntserv.services.calculate import (
    bmr_cunningham,
    bmr_harris_benedict,
    bmr_katch_mcardle,
    bmr_mifflin_st_jeor,
)
from ntserv.utils import cache


def GET_nutrients(request, response_type="JSON"):
    nutrients = list(cache.NUTRIENTS.values())

    if response_type == "JSON":
        return Success200Response(data=nutrients)
    else:  # HTML
        table = tabulate(nutrients, headers="keys", tablefmt="presto")
        return f"<pre>{table}</pre>"


def GET_calc_bmr(request):
    """Calculates all types of BMR for comparison"""
    body = request.json

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


def GET_calc_bmr_katch_mcardle(request):
    """
    BMR = 370 + (21.6 x Lean Body Mass(kg) )
    Source: <https://www.calculatorpro.com/calculator/katch-mcardle-bmr-calculator/>
    Source: <https://tdeecalculator.net/about.php>
    """
    body = request.json

    activity_factor = float(body["activity_factor"])  # ??

    lbm = body.get("lbm")
    if lbm:
        lbm = float(lbm)
    else:
        weight = float(body["weight"])
        bf = float(body["bodyfat"])
        lbm = weight * (1 - bf)

    bmr, tdee = bmr_katch_mcardle(lbm, activity_factor)
    return Success200Response(data={"bmr": round(bmr), "tdee": round(tdee)})


def GET_calc_bmr_cunningham(request):
    """
    Source:
        <https://www.slideshare.net/lsandon/weight-management-in-athletes-lecture>
    """
    body = request.json

    # {'LIGHT': 0.3, 'MODERATE': 0.4, 'HEAVY': 0.5}
    activity_factor = float(body["activity_factor"])

    lbm = body.get("lbm")
    if lbm:
        lbm = float(lbm)
    else:
        weight = float(body["weight"])
        bf = float(body["bodyfat"])
        lbm = weight * (1 - bf)

    bmr, tdee = bmr_cunningham(lbm, activity_factor)
    return Success200Response(data={"bmr": round(bmr), "tdee": round(tdee)})


def GET_calc_bmr_mifflin_st_jeor(request):
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
    body = request.json

    activity_factor = float(body["activity_factor"])
    weight = float(body["weight"])  # kg
    height = float(body["height"])  # cm
    gender = body["gender"]  # ['MALE', 'FEMALE']
    dob = int(body["dob"])  # unix (epoch) timestamp

    bmr, tdee = bmr_mifflin_st_jeor(gender, weight, height, dob, activity_factor)
    return Success200Response(data={"bmr": round(bmr), "tdee": round(tdee)})


def GET_calc_bmr_harris_benedict(request):
    """
    Harris-Benedict = (13.397m + 4.799h - 5.677a) + 88.362 (MEN)
    Harris-Benedict = (9.247m + 3.098h - 4.330a) + 447.593 (WOMEN)

    m is mass in kg, h is height in cm, a is age in years
    Source: <https://tdeecalculator.net/about.php>
    """
    body = request.json

    activity_factor = float(body["activity_factor"])
    weight = float(body["weight"])  # kg
    height = float(body["height"])  # cm
    gender = body["gender"]  # ['MALE', 'FEMALE']
    dob = int(body["dob"])  # unix (epoch) timestamp

    bmr, tdee = bmr_harris_benedict(gender, weight, height, dob, activity_factor)

    return Success200Response(data={"bmr": round(bmr), "tdee": round(tdee)})


def GET_calc_bodyfat(request):
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


def GET_calc_lblimits(request):
    body = request.json
    height = body["height"]

    desired_bf = body.get("desired-bf")

    wrist = body.get("wrist")
    ankle = body.get("ankle")

    # ----------------
    # Martin Berkhan
    # ----------------
    min = round((height - 102) * 2.205, 1)
    max = round((height - 98) * 2.205, 1)
    mb = {"notes": "Contest shape (5-6%)", "weight": f"{min} ~ {max} lbs"}

    # ----------------
    # Eric Helms
    # ----------------
    min = round(4851.00 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
    max = round(5402.25 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
    eh = {"notes": f"{desired_bf}% bodyfat", "weight": f"{min} ~ {max} lbs"}

    # ----------------
    # Casey Butt, PhD
    # ----------------
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
    return Success200Response(
        data={"martin-berkhan": mb, "eric-helms": eh, "casey-butt": cb}
    )
